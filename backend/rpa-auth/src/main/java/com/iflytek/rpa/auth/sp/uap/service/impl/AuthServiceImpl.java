package com.iflytek.rpa.auth.sp.uap.service.impl;

import static com.iflytek.rpa.auth.sp.uap.constants.AuthConstant.NODE_TYPE_MENU;
import static com.iflytek.rpa.auth.sp.uap.constants.AuthConstant.NODE_TYPE_RESOURCE;

import cn.hutool.core.collection.CollectionUtil;
import com.google.common.util.concurrent.ThreadFactoryBuilder;
import com.iflytek.rpa.auth.conf.condition.ConditionalOnSaaSOrUAP;
import com.iflytek.rpa.auth.core.entity.BindResourceDto;
import com.iflytek.rpa.auth.core.entity.RoleAuthResourceDto;
import com.iflytek.rpa.auth.core.service.AuthService;
import com.iflytek.rpa.auth.sp.uap.mapper.TreeNodeMapper;
import com.iflytek.rpa.auth.sp.uap.utils.UapManagementClientUtil;
import com.iflytek.rpa.auth.utils.AppResponse;
import com.iflytek.rpa.auth.utils.ErrorCodeEnum;
import com.iflytek.rpa.auth.utils.TreeComparator;
import com.iflytek.sec.uap.client.api.ClientManagementAPI;
import com.iflytek.sec.uap.client.api.UapUserInfoAPI;
import com.iflytek.sec.uap.client.core.dto.ResponseDto;
import com.iflytek.sec.uap.client.core.dto.TreeNode;
import com.iflytek.sec.uap.client.core.dto.authority.BindAuthorityResourceDto;
import com.iflytek.sec.uap.client.core.dto.authority.UapAuthority;
import com.iflytek.sec.uap.client.core.dto.resource.UapResource;
import com.iflytek.sec.uap.client.core.dto.role.BindAuthDto;
import com.iflytek.sec.uap.client.core.dto.role.BindRoleAuthResourceDto;
import java.util.*;
import java.util.concurrent.*;
import java.util.stream.Collectors;
import javax.annotation.PreDestroy;
import javax.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

/**
 * 菜单
 */
@Slf4j
@Service("authService")
@ConditionalOnSaaSOrUAP
public class AuthServiceImpl implements AuthService {

    @Autowired
    private TreeNodeMapper treeNodeMapper;

    /**
     * 当前登录用户在应用中的菜单信息
     * @param request HTTP请求
     * @return 菜单树列表
     */
    @Override
    public AppResponse<List<com.iflytek.rpa.auth.core.entity.TreeNode>> getUserAuthTreeInApp(
            HttpServletRequest request) {
        // 当前登录用户在应用中的菜单信息
        List<UapAuthority> authList = UapUserInfoAPI.getMenuListList(request);
        List<TreeNode> uapTreeNodeList = buildMenuTree("0", authList);
        // 将UAP的TreeNode列表转换为core的TreeNode列表
        List<com.iflytek.rpa.auth.core.entity.TreeNode> treeNodeList = treeNodeMapper.fromUapTreeNodes(uapTreeNodeList);
        return AppResponse.success(treeNodeList);
    }

    public List<TreeNode> buildMenuTree(String rootId, List<UapAuthority> authList) {

        Map<String, TreeNode> nodeMap = new HashMap<>(authList.size() * 2);
        List<TreeNode> allNodes = new ArrayList<>();
        // 第一次循环：创建所有节点并找到根节点
        for (UapAuthority authority : authList) {
            TreeNode node = convertToTreeNode(authority);
            allNodes.add(node);
            nodeMap.put(node.getId(), node);
        }
        // 第二次循环：构建树结构
        // 构建树结构：将子节点挂载到父节点下
        List<TreeNode> rootNodes = new ArrayList<>();
        for (TreeNode node : allNodes) {
            String parentId = node.getPid();
            if (rootId.equals(parentId)) {
                // 如果是根节点（parentId为0），直接加入根节点列表
                rootNodes.add(node);
            } else {
                // 找到父节点，并将当前节点加入父节点的子节点列表
                TreeNode parent = nodeMap.get(parentId);
                if (parent != null) {
                    parent.getNodes().add(node);
                }
            }
        }
        // 3. 对每个节点的子节点列表按 sort 字段排序
        // 注意：遍历所有节点，但只有包含子节点的节点会实际执行排序
        for (TreeNode node : allNodes) {
            List<TreeNode> children = node.getNodes();
            if (!CollectionUtil.isEmpty(children)) {
                // 使用 sort 字段升序排序
                children.sort(
                        Comparator.comparing(TreeNode::getSort, Comparator.nullsFirst(Comparator.naturalOrder())));
            }
        }
        return rootNodes;
    }

    // 辅助方法：将 UapAuthority 转换为 TreeNode
    private TreeNode convertToTreeNode(UapAuthority authority) {
        TreeNode node = new TreeNode();
        node.setId(authority.getId());
        node.setName(authority.getName());
        node.setPid(authority.getParentId());
        node.setSort(authority.getSort());
        node.setValue(authority.getUrl());
        return node;
    }

    /**
     * 查询菜单、权限树
     * @param roleId 角色ID
     * @param request HTTP请求
     * @return 菜单权限树
     */
    @Override
    public AppResponse<com.iflytek.rpa.auth.core.entity.TreeNode> getAuthResourceTreeInApp(
            String roleId, HttpServletRequest request) {
        if (null == roleId) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "缺少角色id");
        }
        // 应用内全量菜单数据
        List<UapAuthority> menuList = UapUserInfoAPI.getMenuListList(request);
        // 勾选的菜单数据
        String tenantId = UapUserInfoAPI.getTenantId(request);
        List<UapAuthority> checkedAuthList = ClientManagementAPI.queryAuthorityListByRoleId(tenantId, roleId);
        // 勾选的菜单数据根据菜单id分组
        Set<String> checkedAuthIdSet =
                checkedAuthList.stream().map(UapAuthority::getId).collect(Collectors.toSet());
        // 根据id和parentId组装菜单树
        List<String> leafNodeAuthIdList = new ArrayList<>();
        TreeNode treeAuthNode = buildTree("0", menuList, checkedAuthIdSet, leafNodeAuthIdList);
        // 查询勾选的资源数据
        ResponseDto<List<UapResource>> checkedResourceListResponse =
                UapManagementClientUtil.queryResourceListByRoleId(roleId, request);
        if (!checkedResourceListResponse.isFlag()) {
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, checkedResourceListResponse.getMessage());
        }
        List<UapResource> checkedResourceList = checkedResourceListResponse.getData();
        // 根据resourceId分组
        Set<String> checkedResourceIdSet =
                checkedResourceList.stream().map(UapResource::getId).collect(Collectors.toSet());
        // 多线程异步查询资源权限
        Map<String, List<TreeNode>> authResourceMap = new ConcurrentHashMap<>();
        List<CompletableFuture<Void>> futures = new ArrayList<>();

        for (String leafNodeAuthId : leafNodeAuthIdList) {
            CompletableFuture<Void> future = CompletableFuture.supplyAsync(
                            () -> {
                                // 查询该叶子节点下的资源列表
                                return ClientManagementAPI.queryResourceListByAuthId(tenantId, leafNodeAuthId);
                            },
                            RESOURCE_QUERY_EXECUTOR)
                    .thenAcceptAsync(
                            checkResourceList -> {
                                // 转换为TreeNode并设置勾选状态
                                List<TreeNode> resourceNodeList = new ArrayList<>();
                                for (UapResource resource : checkResourceList) {
                                    TreeNode treeResourceNode =
                                            convertResourceToTreeNode(resource, leafNodeAuthId, NODE_TYPE_RESOURCE);
                                    treeResourceNode.setChecked(
                                            checkedResourceIdSet.contains(treeResourceNode.getId()));
                                    resourceNodeList.add(treeResourceNode);
                                }
                                if (!resourceNodeList.isEmpty()) {
                                    authResourceMap.put(leafNodeAuthId, resourceNodeList);
                                }
                            },
                            RESOURCE_QUERY_EXECUTOR);

            futures.add(future);
        }
        // 等待所有异步任务完成
        try {
            CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).get(5, TimeUnit.SECONDS);
        } catch (InterruptedException | ExecutionException | TimeoutException e) {
            Thread.currentThread().interrupt();
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "资源权限查询超时");
        }

        // 使用BFS设置资源节点
        setAuthResourceViaBFS(treeAuthNode, authResourceMap);

        // 将UAP的TreeNode转换为core的TreeNode
        com.iflytek.rpa.auth.core.entity.TreeNode coreTreeNode = treeNodeMapper.fromUapTreeNode(treeAuthNode);
        return AppResponse.success(coreTreeNode);
    }

    // 广度优先遍历实现
    private void setAuthResourceViaBFS(TreeNode root, Map<String, List<TreeNode>> authResourceMap) {
        Queue<TreeNode> queue = new LinkedList<>();
        queue.offer(root);
        while (!queue.isEmpty()) {
            TreeNode node = queue.poll();
            List<TreeNode> resources = authResourceMap.get(node.getId());
            if (resources != null && !resources.isEmpty()) {
                node.getNodes().addAll(resources);
                node.setHasNodes(true);
            }
            queue.addAll(node.getNodes());
        }
    }

    public TreeNode buildTree(
            String rootId, List<UapAuthority> menuList, Set<String> checkedAuthIdSet, List<String> leafNodeAuthIdList) {
        Map<String, TreeNode> nodeMap = new HashMap<>(menuList.size() * 2);
        TreeNode rootNode = null;
        // 第一次循环：创建所有节点并找到根节点
        for (UapAuthority authority : menuList) {
            TreeNode node = convertAuthToTreeNode(authority, NODE_TYPE_MENU);
            node.setChecked(checkedAuthIdSet.contains(authority.getId())); // 简化判断
            nodeMap.put(authority.getId(), node);

            if (rootId.equals(authority.getParentId())) {
                rootNode = node;
            }
        }
        // 第二次循环：构建树结构并标记叶子节点
        for (UapAuthority authority : menuList) {
            String parentId = authority.getParentId();
            if (rootId.equals(parentId)) continue;

            TreeNode node = nodeMap.get(authority.getId());
            TreeNode parent = nodeMap.get(parentId);

            if (parent != null) {
                parent.getNodes().add(node);
                parent.setHasNodes(true);
            }
        }
        // 收集叶子节点（优化为并行流）
        nodeMap.values().parallelStream()
                .filter(node -> node.getNodes().isEmpty())
                .forEach(node -> leafNodeAuthIdList.add(node.getId()));
        return rootNode;
    }

    private TreeNode convertAuthToTreeNode(UapAuthority authority, String nodeType) {
        TreeNode node = new TreeNode();
        doConvertAuthToTreeNode(node, authority, nodeType);
        return node;
    }

    private void doConvertAuthToTreeNode(TreeNode node, UapAuthority authority, String nodeType) {
        // 重置对象状态
        node.setId(authority.getId());
        node.setName(authority.getName());
        node.setPid(authority.getParentId());
        node.setSort(authority.getSort());
        node.setValue(nodeType);
        node.setHasNodes(false); // 初始设置为false，后续会根据子节点情况更新
    }

    private TreeNode convertResourceToTreeNode(UapResource resource, String authId, String nodeType) {
        TreeNode node = new TreeNode();
        doConvertResourceToTreeNode(node, resource, authId, nodeType);
        return node;
    }

    private void doConvertResourceToTreeNode(TreeNode node, UapResource resource, String authId, String nodeType) {
        // 重置对象状态
        node.setId(resource.getId());
        node.setName(resource.getName());
        node.setPid(authId);
        node.setSort(resource.getSort());
        node.setValue(nodeType);
        node.setHasNodes(false); // 初始设置为false，后续会根据子节点情况更新
    }

    // 根据CPU核心数动态设置线程数（建议值：CPU核心数 * 2）
    private static final ExecutorService RESOURCE_QUERY_EXECUTOR = Executors.newFixedThreadPool(
            Runtime.getRuntime().availableProcessors() * 2, // 根据CPU核心数动态设置
            new ThreadFactoryBuilder()
                    .setNameFormat("RoleManage-resource-query-thread-%d")
                    .build());

    @PreDestroy
    public void shutdown() {
        RESOURCE_QUERY_EXECUTOR.shutdownNow();
    }

    /**
     * 保存菜单、资源树
     * @param roleAuthResourceDto 角色权限资源DTO
     * @param request HTTP请求
     * @return 操作结果
     */
    @Override
    public AppResponse<String> saveRoleAuth(RoleAuthResourceDto roleAuthResourceDto, HttpServletRequest request) {
        // 获取保存前的菜单权限树
        AppResponse<com.iflytek.rpa.auth.core.entity.TreeNode> originalTreeResponse =
                getAuthResourceTreeInApp(roleAuthResourceDto.getRoleId(), request);
        if (!originalTreeResponse.ok()) {
            // 类型转换：将 AppResponse<TreeNode> 的错误响应转换为 AppResponse<String>
            // 错误响应中 data 字段不重要，重要的是 code 和 message
            return AppResponse.error(originalTreeResponse.getCode(), originalTreeResponse.getMessage());
        }
        com.iflytek.rpa.auth.core.entity.TreeNode originalTree = originalTreeResponse.getData();
        TreeNode uapTreeNode = treeNodeMapper.toUapTreeNode(originalTree);
        TreeComparator comparator = new TreeComparator();
        // core实体类转uap实体类
        TreeNode mapperUapTreeNode = treeNodeMapper.toUapTreeNode(roleAuthResourceDto.getTreeNode());
        TreeComparator.CompareResult result = comparator.compareTrees(uapTreeNode, mapperUapTreeNode);
        // 获取取消勾选的资源和菜单
        List<String> canceledResources = result.getResourceCancel();
        List<String> canceledMenus = result.getMenuCancel();
        // 获取新勾选的菜单和资源
        Map<String, BindAuthorityResourceDto> newBindingMap = result.getAuthMap();
        //        log.info("返回响应：{}, {}",canceledResources,canceledMenus);
        String tenantId = UapUserInfoAPI.getTenantId(request);
        // 保存之前先把取消勾选的做解绑操作
        // 解绑资源
        if (!CollectionUtil.isEmpty(canceledResources)) {
            BindResourceDto bindResourceDto = new BindResourceDto();

            bindResourceDto.setRoleId(roleAuthResourceDto.getRoleId());
            bindResourceDto.setTenantId(tenantId);
            bindResourceDto.setResourceIds(canceledResources);

            ResponseDto<Object> unBindRoleResourceResponse =
                    UapManagementClientUtil.unBindRoleResource(tenantId, bindResourceDto, request);
            if (!unBindRoleResourceResponse.isFlag()) {
                log.error("解绑资源失败：{}", unBindRoleResourceResponse.getMessage());
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, unBindRoleResourceResponse.getMessage());
            }
        }
        // 解绑菜单
        if (!CollectionUtil.isEmpty(canceledMenus)) {
            BindAuthDto bindAuthDto = new BindAuthDto();
            bindAuthDto.setRoleId(roleAuthResourceDto.getRoleId());
            bindAuthDto.setAuthIdList(canceledMenus);
            ResponseDto<Object> unbindRoleAuthResponse = ClientManagementAPI.unbindRoleAuth(tenantId, bindAuthDto);
            if (!unbindRoleAuthResponse.isFlag()) {
                log.error("解绑菜单失败：{}", unbindRoleAuthResponse.getMessage());
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, unbindRoleAuthResponse.getMessage());
            }
        }
        // 绑定用户新勾选的菜单和资源
        Collection<BindAuthorityResourceDto> authorityResourceList = newBindingMap.values();
        if (!CollectionUtil.isEmpty(authorityResourceList)) {
            BindRoleAuthResourceDto bindRoleAuthResourceDto = new BindRoleAuthResourceDto();
            bindRoleAuthResourceDto.setRoleId(roleAuthResourceDto.getRoleId());
            bindRoleAuthResourceDto.setAuthorityResources(new ArrayList<>(authorityResourceList));
            ResponseDto<Object> saveResponse = ClientManagementAPI.bindRoleAuthResource(
                    UapUserInfoAPI.getTenantId(request), bindRoleAuthResourceDto);
            if (!saveResponse.isFlag()) {
                log.error("绑定菜单资源失败：{}", saveResponse.getMessage());
            }
        }

        return AppResponse.success("保存成功");
    }
}
