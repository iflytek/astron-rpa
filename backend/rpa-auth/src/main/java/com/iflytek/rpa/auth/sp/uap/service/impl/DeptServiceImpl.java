package com.iflytek.rpa.auth.sp.uap.service.impl;

import static com.iflytek.rpa.auth.sp.uap.constants.AuthConstant.ORG_TYPE_DEPT;
import static com.iflytek.rpa.auth.sp.uap.constants.RedisKeyConstant.*;
import static com.iflytek.rpa.auth.utils.RedisUtil.deleteRedisKeysByPrefix;

import cn.hutool.core.collection.CollectionUtil;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.iflytek.rpa.auth.conf.condition.ConditionalOnSaaSOrUAP;
import com.iflytek.rpa.auth.core.entity.*;
import com.iflytek.rpa.auth.core.service.DeptService;
import com.iflytek.rpa.auth.sp.uap.dao.DeptDao;
import com.iflytek.rpa.auth.sp.uap.mapper.*;
import com.iflytek.rpa.auth.sp.uap.utils.DeptUtils;
import com.iflytek.rpa.auth.sp.uap.utils.TenantUtils;
import com.iflytek.rpa.auth.sp.uap.utils.UapManagementClientUtil;
import com.iflytek.rpa.auth.utils.AppResponse;
import com.iflytek.rpa.auth.utils.ErrorCodeEnum;
import com.iflytek.rpa.auth.utils.RedisUtils;
import com.iflytek.sec.uap.client.api.ClientManagementAPI;
import com.iflytek.sec.uap.client.api.UapUserInfoAPI;
import com.iflytek.sec.uap.client.core.client.ManagementClient;
import com.iflytek.sec.uap.client.core.dto.PageDto;
import com.iflytek.sec.uap.client.core.dto.ResponseDto;
import com.iflytek.sec.uap.client.core.dto.TreeNode;
import com.iflytek.sec.uap.client.core.dto.extand.UapExtendPropertyDto;
import com.iflytek.sec.uap.client.core.dto.org.GetOrgTreeDto;
import com.iflytek.sec.uap.client.core.dto.org.UapOrg;
import com.iflytek.sec.uap.client.core.dto.org.UpdateOrgDto;
import com.iflytek.sec.uap.client.core.dto.org.UpdateUapOrgDto;
import com.iflytek.sec.uap.client.core.dto.tenant.UapTenant;
import com.iflytek.sec.uap.client.core.dto.user.ListUserDto;
import com.iflytek.sec.uap.client.core.dto.user.UapUser;
import java.util.*;
import java.util.stream.Collectors;
import javax.servlet.http.HttpServletRequest;
import javax.validation.constraints.NotNull;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.ApplicationContext;
import org.springframework.stereotype.Service;
import org.springframework.util.CollectionUtils;

/**
 * @author mjren
 * @date 2025-03-11 9:43
 * @copyright Copyright (c) 2025 mjren
 */
@Slf4j
@Service("deptService")
@ConditionalOnSaaSOrUAP
public class DeptServiceImpl implements DeptService {
    @Value("${uap.database.name:uap_db}")
    private String databaseName;

    @Autowired
    DeptDao deptDao;

    @Autowired
    private DeleteCommonDtoMapper deleteCommonDtoMapper;

    @Autowired
    private OrgMapper orgMapper;

    @Autowired
    private TreeNodeMapper treeNodeMapper;

    @Autowired
    private ApplicationContext applicationContext;

    @Autowired
    private UpdateOrgDtoMapper updateOrgDtoMapper;

    @Autowired
    private UapExtendPropertyDtoMapper uapExtendPropertyDtoMapper;

    //    @Override
    //    public PageDto<UapOrg> queryOrgPageList(String tenantId, OrgListDto dto, HttpServletRequest request) {
    ////        ManagementClient managementClient = UapManagementClientUtil.getManagementClient(request);
    ////        ResponseDto<PageDto<UapOrg>> orgPageResponse = managementClient.queryOrgPageList(dto);
    //        ResponseDto<PageDto<UapOrg>> orgPageResponse = UapManagementClientUtil.queryOrgPageList(tenantId, dto,
    // request);
    //        if (!orgPageResponse.isFlag()) {
    //            log.error("queryOrgPageList error, msg:{}", orgPageResponse.getMessage());
    //            throw new ServiceException(orgPageResponse.getMessage());
    //        }
    //        return orgPageResponse.getData();
    //    }

    /**
     * 查询部门树、人数、负责人
     * @param request HTTP请求
     * @return 部门树和人员信息
     */
    @Override
    public AppResponse<?> treeAndPerson(HttpServletRequest request) {
        String tenantId = UapUserInfoAPI.getTenantId(request);
        UapUser uapUser = UapUserInfoAPI.getLoginUser(request);
        UapOrg uapOrg =
                ClientManagementAPI.queryOrgByLoginName(tenantId, null == uapUser ? null : uapUser.getLoginName());
        if (null == uapOrg) {
            log.info("treeAndPerson,用户未绑定部门");
            return AppResponse.success(null);
        }
        String firstLevelId = uapOrg.getFirstLevelId();
        // 根据id查最顶层部门信息
        List<UapOrg> firstDeptList =
                ClientManagementAPI.queryOrgListByOrgIds(tenantId, Collections.singletonList(firstLevelId));
        List<UapOrg> deptList = ClientManagementAPI.queryOrgListByParentOrgId(tenantId, firstLevelId);
        deptList.addAll(firstDeptList);
        Map<String, Long> deptPersonNumMap = new HashMap<>();
        List<String> deptUserIdList = new ArrayList<>();
        Map<String, UapUser> deptLeaderMap = new HashMap<>();
        // 查询每个部门有多少人 多线程
        //        分页查用户基本信息列表
        deptList.parallelStream().forEach(dept -> {
            ListUserDto listUserDto = new ListUserDto();
            listUserDto.setStatus(null);
            listUserDto.setOrgId(dept.getId());
            PageDto<UapUser> userListPage = ClientManagementAPI.queryUserPageList(tenantId, listUserDto);
            deptPersonNumMap.put(dept.getId(), userListPage.getTotalCount());

            // 获取部门负责人id
            String deptUserId = dept.getRemark();
            if (StringUtils.isNotBlank(deptUserId)) {
                deptUserIdList.add(deptUserId);
            }
        });

        // 查询每个部门的负责人名称
        ListUserDto listUserDto = new ListUserDto();
        listUserDto.setStatus(null);
        listUserDto.setUserIds(deptUserIdList);
        PageDto<UapUser> userListPage =
                ClientManagementAPI.queryUserPageList(UapUserInfoAPI.getTenantId(request), listUserDto);
        if (!CollectionUtils.isEmpty(userListPage.getResult())) {
            for (UapUser deptLeader : userListPage.getResult()) {
                deptLeaderMap.put(deptLeader.getId(), deptLeader);
            }
        }

        // 构建部门树，并将人数和人名组装到部门树中
        List<DeptTreeNodeDto> treeNodeList = buildMenuTree("0", deptList, deptPersonNumMap, deptLeaderMap);

        // 查询租户名称
        UapTenant tenantInfo = UapUserInfoAPI.getTenant(request);
        if (null == tenantInfo) {
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "无租户信息");
        }
        Map<String, Object> result = new HashMap<>();
        result.put("tenantName", tenantInfo.getName());
        result.put("deptTree", treeNodeList);
        return AppResponse.success(result);
    }

    /**
     * 优化版本的部门树和人员查询
     * 包含以下优化：
     * 1. 只返回必要字段（name, userNum, userName, id, orgId, pid）
     * 2. 使用Redis缓存，缓存时间1小时
     * 3. 只查询顶级部门和次级部门
     * 4. 优化并行查询逻辑
     *
     * @param request HTTP请求
     * @return 优化后的响应结果
     */
    public AppResponse<Map<String, Object>> treeAndPersonOptimized(HttpServletRequest request) {
        String tenantId = UapUserInfoAPI.getTenantId(request);
        UapUser uapUser = UapUserInfoAPI.getLoginUser(request);

        // 构建缓存key（两层限制版本）
        String cacheKey =
                "dept:tree:two-level:" + tenantId + ":" + (uapUser != null ? uapUser.getLoginName() : "anonymous");

        // 先尝试从Redis获取缓存数据
        try {
            Object cachedObj = RedisUtils.get(cacheKey);
            if (cachedObj != null) {
                log.info("从Redis缓存获取两层部门树数据: {}", cacheKey);
                ObjectMapper objectMapper = new ObjectMapper();
                @SuppressWarnings("unchecked")
                Map<String, Object> cachedResult = objectMapper.readValue(cachedObj.toString(), Map.class);
                return AppResponse.success(cachedResult);
            }
        } catch (Exception e) {
            log.warn("Redis缓存读取失败，继续查询数据库: {}", e.getMessage());
        }

        UapOrg uapOrg =
                ClientManagementAPI.queryOrgByLoginName(tenantId, null == uapUser ? null : uapUser.getLoginName());
        if (null == uapOrg) {
            log.info("treeAndPersonOptimized,用户未绑定部门");
            return AppResponse.success(null);
        }

        String firstLevelId = uapOrg.getFirstLevelId();

        // 查询租户名称
        UapTenant tenantInfo = UapUserInfoAPI.getTenant(request);
        if (null == tenantInfo) {
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "无租户信息");
        }

        // 只查询顶级部门和次级部门，减少数据量
        List<UapOrg> topLevelDepts =
                ClientManagementAPI.queryOrgListByOrgIds(tenantId, Collections.singletonList(firstLevelId));
        List<UapOrg> secondLevelDepts = ClientManagementAPI.queryOrgListByParentOrgId(tenantId, firstLevelId);

        // 合并顶级和次级部门
        List<UapOrg> deptList = new ArrayList<>();
        deptList.addAll(topLevelDepts);
        deptList.addAll(secondLevelDepts);

        // 优化的并行查询：只查询人数和负责人信息
        Map<String, Long> deptPersonNumMap = new HashMap<>();
        List<String> deptUserIdList = Collections.synchronizedList(new ArrayList<>());
        Map<String, UapUser> deptLeaderMap = new HashMap<>();

        // 并行查询每个部门的人数和负责人ID
        deptList.parallelStream().forEach(dept -> {
            // 查询部门人数
            ListUserDto listUserDto = new ListUserDto();
            listUserDto.setStatus(null);
            listUserDto.setOrgId(dept.getId());
            PageDto<UapUser> userListPage = ClientManagementAPI.queryUserPageList(tenantId, listUserDto);

            synchronized (deptPersonNumMap) {
                deptPersonNumMap.put(dept.getId(), userListPage.getTotalCount());
            }

            // 收集部门负责人ID
            String deptUserId = dept.getRemark();
            if (StringUtils.isNotBlank(deptUserId)) {
                deptUserIdList.add(deptUserId);
            }
        });

        // 批量查询所有部门负责人信息
        if (!deptUserIdList.isEmpty()) {
            ListUserDto listUserDto = new ListUserDto();
            listUserDto.setStatus(null);
            listUserDto.setUserIds(deptUserIdList);
            PageDto<UapUser> userListPage = ClientManagementAPI.queryUserPageList(tenantId, listUserDto);
            if (!CollectionUtils.isEmpty(userListPage.getResult())) {
                for (UapUser deptLeader : userListPage.getResult()) {
                    deptLeaderMap.put(deptLeader.getId(), deptLeader);
                }
            }
        }

        // 构建简化的部门树（限制为两层）
        List<SimpleDeptTreeNodeDto> treeNodeList =
                buildSimpleTwoLevelDeptTree(firstLevelId, deptList, deptPersonNumMap, deptLeaderMap);

        // 构建响应结果
        Map<String, Object> result = new HashMap<>();
        result.put("tenantName", tenantInfo.getName());
        result.put("deptTree", treeNodeList);

        // 将结果缓存到Redis，缓存1小时
        try {
            ObjectMapper objectMapper = new ObjectMapper();
            String resultJson = objectMapper.writeValueAsString(result);
            RedisUtils.set(cacheKey, resultJson, 3600); // 1小时缓存
            log.info("两层部门树数据已缓存到Redis: {}", cacheKey);
        } catch (Exception e) {
            log.warn("Redis缓存写入失败: {}", e.getMessage());
        }

        return AppResponse.success(result);
    }

    public List<DeptTreeNodeDto> buildMenuTree(
            String rootId,
            List<UapOrg> deptList,
            Map<String, Long> deptPersonNumMap,
            Map<String, UapUser> deptLeaderMap) {

        Map<String, DeptTreeNodeDto> nodeMap = new HashMap<>(deptList.size() * 2);
        List<DeptTreeNodeDto> allNodes = new ArrayList<>();
        // 第一次循环：创建所有节点并找到根节点
        for (UapOrg dept : deptList) {
            DeptTreeNodeDto node = convertToTreeNode(dept, deptPersonNumMap, deptLeaderMap);
            allNodes.add(node);
            nodeMap.put(node.getId(), node);
        }
        // 第二次循环：构建树结构
        // 构建树结构：将子节点挂载到父节点下
        List<DeptTreeNodeDto> rootNodes = new ArrayList<>();
        for (DeptTreeNodeDto node : allNodes) {
            String parentId = node.getPid();
            if (rootId.equals(parentId)) {
                // 如果是根节点（parentId为0），直接加入根节点列表
                rootNodes.add(node);
            } else {
                // 找到父节点，并将当前节点加入父节点的子节点列表
                DeptTreeNodeDto parent = nodeMap.get(parentId);
                if (parent != null) {
                    parent.getNodes().add(node);
                }
            }
        }
        // 3. 对每个节点的子节点列表按 sort 字段排序
        // 注意：遍历所有节点，但只有包含子节点的节点会实际执行排序
        for (DeptTreeNodeDto node : allNodes) {
            List<DeptTreeNodeDto> children = node.getNodes();
            if (!CollectionUtil.isEmpty(children)) {
                // 使用 sort 字段升序排序
                children.sort(Comparator.comparing(
                        DeptTreeNodeDto::getSort, Comparator.nullsFirst(Comparator.naturalOrder())));
            }
        }
        return rootNodes;
    }

    /**
     * 构建简化的两层部门树（顶级部门 + 次级部门）
     */
    public List<SimpleDeptTreeNodeDto> buildSimpleTwoLevelDeptTree(
            String topLevelId,
            List<UapOrg> deptList,
            Map<String, Long> deptPersonNumMap,
            Map<String, UapUser> deptLeaderMap) {
        List<SimpleDeptTreeNodeDto> rootNodes = new ArrayList<>();

        // 找到顶级部门
        UapOrg topDept = deptList.stream()
                .filter(dept -> topLevelId.equals(dept.getId()))
                .findFirst()
                .orElse(null);

        if (topDept == null) {
            log.warn("未找到顶级部门: {}", topLevelId);
            return rootNodes;
        }

        // 创建顶级部门节点
        SimpleDeptTreeNodeDto topNode = convertToSimpleTreeNode(topDept, deptPersonNumMap, deptLeaderMap);

        // 找到所有次级部门（父部门为topLevelId的部门）
        List<SimpleDeptTreeNodeDto> secondLevelNodes = deptList.stream()
                .filter(dept -> topLevelId.equals(dept.getHigherOrg()))
                .map(dept -> convertToSimpleTreeNode(dept, deptPersonNumMap, deptLeaderMap))
                .sorted(Comparator.comparing(SimpleDeptTreeNodeDto::getName))
                .collect(Collectors.toList());

        // 将次级部门挂载到顶级部门下
        topNode.setNodes(secondLevelNodes);
        rootNodes.add(topNode);

        return rootNodes;
    }

    /**
     * 构建简化的部门树（只包含必要字段）
     */
    public List<SimpleDeptTreeNodeDto> buildSimpleDeptTree(
            String rootId,
            List<UapOrg> deptList,
            Map<String, Long> deptPersonNumMap,
            Map<String, UapUser> deptLeaderMap) {
        Map<String, SimpleDeptTreeNodeDto> nodeMap = new HashMap<>(deptList.size() * 2);
        List<SimpleDeptTreeNodeDto> allNodes = new ArrayList<>();

        // 第一次循环：创建所有节点
        for (UapOrg dept : deptList) {
            SimpleDeptTreeNodeDto node = convertToSimpleTreeNode(dept, deptPersonNumMap, deptLeaderMap);
            allNodes.add(node);
            nodeMap.put(node.getId(), node);
        }

        // 第二次循环：构建树结构
        List<SimpleDeptTreeNodeDto> rootNodes = new ArrayList<>();
        for (SimpleDeptTreeNodeDto node : allNodes) {
            String parentId = node.getPid();
            if (rootId.equals(parentId)) {
                // 顶级节点
                rootNodes.add(node);
            } else {
                // 找到父节点，并将当前节点加入父节点的子节点列表
                SimpleDeptTreeNodeDto parent = nodeMap.get(parentId);
                if (parent != null) {
                    parent.getNodes().add(node);
                }
            }
        }

        // 对每个节点的子节点按排序字段排序（如果需要的话，这里简化处理）
        for (SimpleDeptTreeNodeDto node : allNodes) {
            List<SimpleDeptTreeNodeDto> children = node.getNodes();
            if (!CollectionUtil.isEmpty(children)) {
                // 简单按名称排序
                children.sort(Comparator.comparing(SimpleDeptTreeNodeDto::getName));
            }
        }

        return rootNodes;
    }

    /**
     * 将 UapOrg 转换为 SimpleDeptTreeNodeDto
     */
    private SimpleDeptTreeNodeDto convertToSimpleTreeNode(
            UapOrg dept, Map<String, Long> deptPersonNumMap, Map<String, UapUser> deptLeaderMap) {
        SimpleDeptTreeNodeDto node = new SimpleDeptTreeNodeDto();
        node.setId(dept.getId());
        node.setOrgId(dept.getId()); // orgId与id保持一致
        node.setName(dept.getName());
        node.setPid(dept.getHigherOrg());
        node.setUserNum(deptPersonNumMap.getOrDefault(dept.getId(), 0L));

        // 设置部门负责人名称
        UapUser leaderInfo = deptLeaderMap.get(dept.getRemark());
        if (leaderInfo != null) {
            node.setUserName(leaderInfo.getName());
        }

        return node;
    }

    // 辅助方法：将 UapAuthority 转换为 DeptTreeNodeDto
    private DeptTreeNodeDto convertToTreeNode(
            UapOrg dept, Map<String, Long> deptPersonNumMap, Map<String, UapUser> deptLeaderMap) {
        DeptTreeNodeDto node = new DeptTreeNodeDto();
        node.setId(dept.getId());
        node.setName(dept.getName());
        node.setPid(dept.getHigherOrg());
        node.setSort(dept.getSort());
        node.setUserNum(deptPersonNumMap.getOrDefault(dept.getId(), 0L));
        UapUser leaderInfo = deptLeaderMap.get(dept.getRemark());
        if (null != leaderInfo) {
            node.setUserId(leaderInfo.getId());
            node.setUserName(leaderInfo.getName());
        }
        return node;
    }

    /**
     * 新增部门
     * @param createUapOrgDto 创建部门DTO
     * @param request HTTP请求
     * @return 操作结果
     */
    @Override
    public AppResponse<String> addDept(CreateUapOrgDto createUapOrgDto, HttpServletRequest request) {
        if (null == createUapOrgDto.getUapOrg()
                || StringUtils.isBlank(createUapOrgDto.getUapOrg().getName())
                || StringUtils.isBlank(createUapOrgDto.getUapOrg().getHigherOrg())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        createUapOrgDto.getUapOrg().setOrgType(ORG_TYPE_DEPT);
        ManagementClient managementClient = UapManagementClientUtil.getManagementClient(request);

        // 通用实体类转换到uap实体类
        CreateUapOrgDtoMapper createUapOrgDtoMapper = new CreateUapOrgDtoMapper();
        com.iflytek.sec.uap.client.core.dto.org.CreateUapOrgDto uapCreateUapOrgDto =
                createUapOrgDtoMapper.toUapCreateUapOrgDto(createUapOrgDto);

        ResponseDto<String> addResponse = managementClient.addOrg(uapCreateUapOrgDto);
        if (!addResponse.isFlag()) {
            log.error("addOrg error, msg:{}", addResponse.getMessage());
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, addResponse.getMessage());
        }

        // 删除所有以"dept:"为前缀的Redis数据
        deleteRedisKeysByPrefix(REDIS_KEY_DEPT_PREFIX);
        return AppResponse.success(addResponse.getData());
    }

    /**
     * 获取部门树 todo 只返回有权限的
     * @param request HTTP请求
     * @return 部门树
     * @throws Exception 异常
     */
    @Override
    public AppResponse<com.iflytek.rpa.auth.core.entity.TreeNode> queryTreeList(HttpServletRequest request)
            throws Exception {
        String tenantId = UapUserInfoAPI.getTenantId(request);
        String key = REDIS_KEY_DEPT_PREFIX + tenantId;
        log.info("redis查询部门信息[dept:tenantId]：" + key);
        Object cachedObj = RedisUtils.get(key);
        String cached = cachedObj != null ? cachedObj.toString() : null;
        if (StringUtils.isNotBlank(cached)) {
            ObjectMapper objectMapper = new ObjectMapper();
            TreeNode uapTreeNode = objectMapper.readValue(cached, TreeNode.class);
            // 将UAP的TreeNode转换为core的TreeNode
            com.iflytek.rpa.auth.core.entity.TreeNode treeNode = treeNodeMapper.fromUapTreeNode(uapTreeNode);
            return AppResponse.success(treeNode);
        }
        String firstLevelId = "0";
        GetOrgTreeDto getOrgTreeDto = new GetOrgTreeDto();
        getOrgTreeDto.setParentId(firstLevelId);
        ManagementClient managementClient = UapManagementClientUtil.getManagementClient(request);
        ResponseDto<TreeNode> responseDto = managementClient.queryOrgTree(getOrgTreeDto);
        if (!responseDto.isFlag()) {
            log.error("queryOrgTree error, msg:{}", responseDto.getMessage());
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "部门查询失败");
        }
        TreeNode uapData = responseDto.getData();
        // 将UAP的TreeNode转换为core的TreeNode
        com.iflytek.rpa.auth.core.entity.TreeNode coreData = treeNodeMapper.fromUapTreeNode(uapData);
        ObjectMapper objectMapper = new ObjectMapper();
        // 缓存时仍然使用UAP的TreeNode（因为可能其他代码还在使用）
        RedisUtils.set(key, objectMapper.writeValueAsString(uapData), 3600);
        return AppResponse.success(coreData);
    }

    /**
     * 通过部门父节点的id查询所有部门子节点
     * @param dto 查询参数
     * @param request HTTP请求
     * @return 部门子节点列表
     * @throws Exception 异常
     */
    @Override
    public AppResponse<List<DeptTreeNodeVo>> queryDeptTreeByPid(QueryDeptNodeDto dto, HttpServletRequest request)
            throws Exception {
        String tenantId = UapUserInfoAPI.getTenantId(request);
        // 顶级节点
        String pid = dto.getPid();
        // 将 deptTreeNodeVos 存储到 redis
        String redisKey = REDIS_KEY_DEPT_CHILD_NODES_PREFIX + tenantId + ":" + pid;
        // 查询 redis 是否有缓存，如果有则直接从缓存中取
        Object cachedDeptTree = RedisUtils.get(redisKey);
        if (cachedDeptTree != null && StringUtils.isNotBlank(cachedDeptTree.toString())) {
            ObjectMapper objectMapper = new ObjectMapper();
            List<DeptTreeNodeVo> cachedList = objectMapper.readValue(
                    cachedDeptTree.toString(),
                    objectMapper.getTypeFactory().constructCollectionType(List.class, DeptTreeNodeVo.class));
            // 返回缓存数据
            return AppResponse.success(cachedList);
        }
        if (pid.equals("1")) {
            pid = deptDao.queryByHigherDeptId("0", tenantId, databaseName);
            if (StringUtils.isBlank(pid)) {
                return AppResponse.success(new ArrayList<>());
            }
        }
        List<DeptTreeNodeVo> deptTreeNodeVos = deptDao.queryChildrenOrgList(pid, tenantId, databaseName);
        // 设置hasNodes字段
        if (!CollectionUtil.isEmpty(deptTreeNodeVos)) {
            List<String> childrenIds =
                    deptTreeNodeVos.stream().map(DeptTreeNodeVo::getId).collect(Collectors.toList());
            List<String> deptIdsWithChildren = deptDao.queryDeptIdsWithChildren(childrenIds, tenantId, databaseName);
            Set<String> hasChildrenSet = new HashSet<>(deptIdsWithChildren);
            for (DeptTreeNodeVo deptNode : deptTreeNodeVos) {
                deptNode.setHasNodes(hasChildrenSet.contains(deptNode.getId()));
            }
        } else {
            for (DeptTreeNodeVo deptNode : deptTreeNodeVos) {
                deptNode.setHasNodes(false);
            }
        }
        RedisUtils.set(redisKey, new ObjectMapper().writeValueAsString(deptTreeNodeVos), 3600);
        return AppResponse.success(deptTreeNodeVos);
    }

    @Override
    public AppResponse<String> editDept(EditOrgDto editOrgDto, HttpServletRequest request) {
        String userId = editOrgDto.getUserId();
        com.iflytek.rpa.auth.core.entity.UpdateOrgDto updateOrgDto = editOrgDto.getUapOrg();
        if (null == updateOrgDto || StringUtils.isBlank(updateOrgDto.getId())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        // 更新部门负责人
        updateOrgDto.setRemark(userId);
        editOrgDto.setUapOrg(updateOrgDto);

        // 转化UpdateUapOrgDto为uap实体类
        UpdateUapOrgDto updateUapOrgDto = new UpdateUapOrgDto();
        UpdateOrgDto uapUpdateOrgDto = updateOrgDtoMapper.toUapUpdateOrgDto(updateOrgDto);
        updateUapOrgDto.setUapOrg(uapUpdateOrgDto);
        List<UapExtendPropertyDto> uapExtendPropertyDtoList =
                uapExtendPropertyDtoMapper.toUapExtendPropertyDtoList(editOrgDto.getExtands());
        updateUapOrgDto.setExtands(uapExtendPropertyDtoList);

        ManagementClient managementClient = UapManagementClientUtil.getManagementClient(request);
        ResponseDto<String> editResponse = managementClient.updateOrg(updateUapOrgDto);
        if (!editResponse.isFlag()) {
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, editResponse.getMessage());
        }
        // 删除所有以"dept:"为前缀的Redis数据
        deleteRedisKeysByPrefix(REDIS_KEY_DEPT_PREFIX);
        return AppResponse.success(editResponse.getData());
    }

    @Override
    public AppResponse<String> deleteDept(DeleteCommonDto deleteCommonDto, HttpServletRequest request) {
        if (StringUtils.isBlank(deleteCommonDto.getId())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        ManagementClient managementClient = UapManagementClientUtil.getManagementClient(request);

        com.iflytek.sec.uap.client.core.dto.DeleteCommonDto uapDeleteCommonDto =
                deleteCommonDtoMapper.toUapDeleteCommonDto(deleteCommonDto);
        ResponseDto<String> deleteResponse = managementClient.deleteOrg(uapDeleteCommonDto);
        if (!deleteResponse.isFlag()) {
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, deleteResponse.getMessage());
        }
        // 删除所有以"dept:"为前缀的Redis数据
        deleteRedisKeysByPrefix(REDIS_KEY_DEPT_PREFIX);
        return AppResponse.success(deleteResponse.getData());
    }

    /**
     * 通过deptId查询部门名
     * @param dto 查询参数
     * @param request HTTP请求
     * @return 部门名
     */
    @Override
    public AppResponse<DeptNameVo> queryDeptNameByDeptId(QueryDeptIdDto dto, HttpServletRequest request) {
        String deptId = dto.getDeptId();
        if (StringUtils.isBlank(deptId)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        String tenantId = UapUserInfoAPI.getTenantId(request);
        String deptName = deptDao.queryDeptNameByDeptId(deptId, tenantId, databaseName);
        DeptNameVo deptNameVo = new DeptNameVo();
        deptNameVo.setName(deptName);
        return AppResponse.success(deptNameVo);
    }

    @Override
    public AppResponse<String> queryTenantName(HttpServletRequest request) {
        try {
            String tenantName = TenantUtils.getTenantName();
            if (StringUtils.isBlank(tenantName)) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取租户名称失败");
            }
            return AppResponse.success(tenantName);
        } catch (Exception e) {
            log.error("获取租户名称失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取租户名称失败: " + e.getMessage());
        }
    }

    /**
     * 部门人数信息查询
     * @param dto 查询参数
     * @param request HTTP请求
     * @return 部门人数节点列表
     * @throws JsonProcessingException JSON处理异常
     */
    @Override
    public AppResponse<List<DeptPersonTreeNodeVo>> queryDeptPersonNodeByPid(
            QueryDeptNodeDto dto, HttpServletRequest request) throws JsonProcessingException {
        String tenantId = UapUserInfoAPI.getTenantId(request);
        // 顶级节点
        String pid = dto.getPid();
        // 将 deptTreeNodeVos 存储到 redis
        String redisKey = REDIS_KEY_DEPT_PERSON_CHILD_NODES_PREFIX + tenantId + ":" + pid;
        // 查询 redis 是否有缓存，如果有则直接从缓存中取
        Object cachedDeptTree = RedisUtils.get(redisKey);
        if (cachedDeptTree != null && StringUtils.isNotBlank(cachedDeptTree.toString())) {
            ObjectMapper objectMapper = new ObjectMapper();
            List<DeptPersonTreeNodeVo> cachedList = objectMapper.readValue(
                    cachedDeptTree.toString(),
                    objectMapper.getTypeFactory().constructCollectionType(List.class, DeptPersonTreeNodeVo.class));
            // 返回缓存数据
            return AppResponse.success(cachedList);
        }

        if (pid.equals("1")) {
            pid = deptDao.queryByHigherDeptId("0", tenantId, databaseName);
            if (StringUtils.isBlank(pid)) {
                return AppResponse.success(new ArrayList<>());
            }
        }
        List<DeptTreeNodeVo> deptTreeNodeVos = deptDao.queryChildrenOrgList(pid, tenantId, databaseName);

        List<DeptPersonTreeNodeVo> deptPersonTreeNodeVos = new ArrayList<>();

        if (!CollectionUtil.isEmpty(deptTreeNodeVos)) {
            // 设置hasNodes字段
            List<String> childrenIds =
                    deptTreeNodeVos.stream().map(DeptTreeNodeVo::getId).collect(Collectors.toList());
            List<String> deptIdsWithChildren = deptDao.queryDeptIdsWithChildren(childrenIds, tenantId, databaseName);
            Set<String> hasChildrenSet = new HashSet<>(deptIdsWithChildren);
            for (DeptTreeNodeVo deptNode : deptTreeNodeVos) {
                deptNode.setHasNodes(hasChildrenSet.contains(deptNode.getId()));
            }

            Map<String, DeptPersonInfoBo> deptIdToPersonInfo = packageDeptPersonNum(childrenIds, tenantId);

            // 组装 DeptPersonTreeNodeVo 列表
            for (DeptTreeNodeVo deptNode : deptTreeNodeVos) {
                DeptPersonTreeNodeVo personNode = new DeptPersonTreeNodeVo();
                personNode.setId(deptNode.getId());
                personNode.setName(deptNode.getName());
                personNode.setPid(deptNode.getPid());
                personNode.setHasNodes(Boolean.TRUE.equals(deptNode.getHasNodes()));
                DeptPersonInfoBo info = deptIdToPersonInfo.get(deptNode.getId());
                personNode.setUserNum(info != null && info.getUserNum() != null ? info.getUserNum() : 0);
                personNode.setUserName(info != null ? info.getUserName() : null);
                deptPersonTreeNodeVos.add(personNode);
            }
        } else {
            for (DeptTreeNodeVo deptNode : deptTreeNodeVos) {
                deptNode.setHasNodes(false);
            }
        }
        RedisUtils.set(redisKey, new ObjectMapper().writeValueAsString(deptPersonTreeNodeVos), 3600);
        return AppResponse.success(deptPersonTreeNodeVos);
    }

    @NotNull
    private Map<String, DeptPersonInfoBo> packageDeptPersonNum(List<String> deptIds, String tenantId) {
        // 将人数信息转为map，key为部门id
        Map<String, DeptPersonInfoBo> deptIdToPersonInfo = new HashMap<>();
        for (String deptId : deptIds) {
            List<String> matchedIds = deptDao.getMatchedIds(deptId, databaseName);
            //  部门人数
            List<DeptPersonInfoBo> deptPersonInfoBos = deptDao.queryUserNumByOrgIds(matchedIds, tenantId, databaseName);
            // 累加人数
            Integer totalUserNum = deptPersonInfoBos.stream()
                    .filter(Objects::nonNull)
                    .mapToInt(info -> info.getUserNum() != null ? info.getUserNum() : 0)
                    .sum();
            DeptPersonInfoBo deptPersonInfoBo = new DeptPersonInfoBo();
            deptPersonInfoBo.setUserNum(totalUserNum);
            deptIdToPersonInfo.put(deptId, deptPersonInfoBo);
        }
        return deptIdToPersonInfo;
    }

    /**
     * 查询当前机构的所有用户
     * @param dto 查询参数
     * @param request HTTP请求
     * @return 用户列表
     * @throws Exception 异常
     */
    @Override
    public AppResponse<List<UserVo>> queryAllUserByDeptId(QueryDeptIdDto dto, HttpServletRequest request)
            throws Exception {
        String deptId = dto.getDeptId();
        String name = dto.getName();
        if (StringUtils.isBlank(deptId)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        String tenantId = UapUserInfoAPI.getTenantId(request);
        // Redis 缓存 key
        String redisKey = REDIS_KEY_DEPT_ALL_USER_PREFIX + deptId + ":" + (name == null ? "" : name);

        Object cachedObj = RedisUtils.get(redisKey);
        if (cachedObj != null && StringUtils.isNotBlank(cachedObj.toString())) {
            ObjectMapper objectMapper = new ObjectMapper();
            List<UserVo> cachedList = objectMapper.readValue(
                    cachedObj.toString(),
                    objectMapper.getTypeFactory().constructCollectionType(List.class, UserVo.class));
            return AppResponse.success(cachedList);
        }

        List<UserVo> result = deptDao.queryUserListByDeptId(name, deptId, tenantId, databaseName);

        ObjectMapper objectMapper = new ObjectMapper();
        RedisUtils.set(redisKey, objectMapper.writeValueAsString(result), 3600);
        return AppResponse.success(result);
    }

    @Override
    public AppResponse<String> getCurrentLevelCode(HttpServletRequest request) {
        try {
            String levelCode = DeptUtils.getLevelCode();
            //            if (StringUtils.isBlank(levelCode)) {
            //                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取部门levelCode失败");
            //            }
            return AppResponse.success(levelCode);
        } catch (Exception e) {
            log.error("获取当前登录用户的部门levelCode失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取部门levelCode失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<String> getCurrentDeptId(HttpServletRequest request) {
        try {
            String deptId = DeptUtils.getDeptId();
            if (StringUtils.isBlank(deptId)) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取部门ID失败");
            }
            return AppResponse.success(deptId);
        } catch (Exception e) {
            log.error("获取当前登录用户的部门ID失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取部门ID失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<Org> getCurrentDeptInfo(HttpServletRequest request) {
        try {
            UapOrg uapOrg = DeptUtils.getDeptInfo();
            if (uapOrg == null) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取部门信息失败");
            }
            Org org = orgMapper.fromUapOrg(uapOrg);
            return AppResponse.success(org);
        } catch (Exception e) {
            log.error("获取当前登录用户的部门详细信息失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取部门信息失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<Org> getDeptInfoByDeptId(String id, HttpServletRequest request) {
        try {
            if (StringUtils.isBlank(id)) {
                return AppResponse.success(null);
            }
            UapOrg uapOrg = DeptUtils.getDeptInfoByDeptId(id);
            if (uapOrg == null) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "未找到部门信息");
            }
            Org org = orgMapper.fromUapOrg(uapOrg);
            return AppResponse.success(org);
        } catch (Exception e) {
            log.error("根据部门ID查询部门详细信息失败, deptId: {}", id, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "查询部门信息失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<String> getLevelCodeByDeptId(String id, HttpServletRequest request) {
        try {
            if (StringUtils.isBlank(id)) {
                return AppResponse.success("");
            }
            String levelCode = DeptUtils.getLevelCodeByDeptId(id);
            if (StringUtils.isBlank(levelCode)) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取部门levelCode失败");
            }
            return AppResponse.success(levelCode);
        } catch (Exception e) {
            log.error("查询部门ID对应的levelCode失败, deptId: {}", id, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "查询levelCode失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<Long> getUserNumByDeptId(String id, HttpServletRequest request) {
        try {
            if (StringUtils.isBlank(id)) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "部门ID不能为空");
            }
            Long userNum = DeptUtils.getUserNumByDeptId(id);
            if (userNum == null) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "查询用户数量失败");
            }
            return AppResponse.success(userNum);
        } catch (Exception e) {
            log.error("查询指定机构及所有子机构的用户数量失败, deptId: {}", id, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "查询用户数量失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<List<Org>> queryOrgListByIds(List<String> orgIdList, HttpServletRequest request) {
        try {
            if (CollectionUtil.isEmpty(orgIdList)) {
                return AppResponse.success(Collections.emptyList());
            }
            String tenantId = UapUserInfoAPI.getTenantId(request);
            List<UapOrg> uapOrgs = DeptUtils.queryOrgPageList(tenantId, orgIdList);
            List<Org> orgs = orgMapper.fromUapOrgs(uapOrgs);
            return AppResponse.success(orgs);
        } catch (Exception e) {
            log.error("根据部门ID列表获取部门信息列表失败, orgIds: {}", orgIdList, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "查询部门信息列表失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<String> getDeptIdByUserId(String userId, String tenantId, HttpServletRequest request) {
        try {
            if (StringUtils.isBlank(userId)) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "用户ID不能为空");
            }
            if (StringUtils.isBlank(tenantId)) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "租户ID不能为空");
            }
            String deptId = DeptUtils.getDeptIdByUserId(userId, tenantId);
            if (StringUtils.isBlank(deptId)) {
                return AppResponse.success("");
            }
            return AppResponse.success(deptId);
        } catch (Exception e) {
            log.error("根据用户ID获取部门ID失败, userId: {}", userId, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取部门ID失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<DataAuthDetailDo> getDataAuthWithDeptList(HttpServletRequest request) {
        try {
            DataAuthDetailDo dataAuthDetailDo = DeptUtils.getDataAuthWithDeptList();
            return AppResponse.success(dataAuthDetailDo);
        } catch (Exception e) {
            log.error("查询数据权限失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "查询数据权限失败: " + e.getMessage());
        }
    }
}
