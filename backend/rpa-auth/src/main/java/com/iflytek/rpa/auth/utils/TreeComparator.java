package com.iflytek.rpa.auth.utils;

import static com.iflytek.rpa.auth.sp.uap.constants.AuthConstant.NODE_TYPE_MENU;
import static com.iflytek.rpa.auth.sp.uap.constants.AuthConstant.NODE_TYPE_RESOURCE;

import com.iflytek.rpa.auth.conf.condition.ConditionalOnSaaSOrUAP;
import com.iflytek.rpa.auth.exception.ServiceException;
import com.iflytek.sec.uap.client.core.dto.TreeNode;
import com.iflytek.sec.uap.client.core.dto.authority.BindAuthorityResourceDto;
import java.util.*;
import lombok.Data;

/**
 * @author mjren
 * @date 2025-03-05 11:05
 * @copyright Copyright (c) 2025 mjren
 */
@ConditionalOnSaaSOrUAP
public class TreeComparator {

    // 结果容器
    private List<String> resourceCancel = new ArrayList<>();
    private List<String> menuCancel = new ArrayList<>();
    private Map<String, BindAuthorityResourceDto> authMap = new HashMap<>();

    // 节点ID -> 节点对象的映射（用于快速查找）
    private Map<String, TreeNode> modifiedNodeMap = new HashMap<>();

    /**
     * 两颗TreeNode树，第一颗是用户编辑之前的数据，第二颗是用户对菜单和资源取消或新增勾选后的数据，
     * 树结构完全相同，但是每个节点中的checked属性值（true,false）不同，
     * 对比两颗TreeNode树checked属性值，将第二颗树中相比第一颗树，
     * checked为false的叶子节点放到resourceCancel列表里面，
     * checked为false的非叶子节点放到menuCancel列表里面，
     * 相比第一颗树checked为true的叶子节点和他的直接父节点放到Map<String, BindAuthorityResourceDto> authMap里面
     */
    public CompareResult compareTrees(TreeNode originalRoot, TreeNode modifiedRoot) {
        // 步骤1：预构建修改树的节点映射
        buildNodeMap(modifiedRoot);

        // 步骤2：递归比较
        traverseAndCompare(originalRoot, modifiedRoot);
        return new CompareResult(resourceCancel, menuCancel, authMap);
    }

    // 构建节点映射表
    private void buildNodeMap(TreeNode root) {
        Deque<TreeNode> stack = new ArrayDeque<>();
        stack.push(root);
        while (!stack.isEmpty()) {
            TreeNode node = stack.pop();
            modifiedNodeMap.put(node.getId(), node);
            for (TreeNode child : node.getNodes()) {
                stack.push(child);
            }
        }
    }

    private void traverseAndCompare(TreeNode originalNode, TreeNode modifiedNode) {
        if (originalNode == null || modifiedNode == null) return;

        // 对比checked状态变化
        boolean originalChecked = Boolean.TRUE.equals(originalNode.getChecked());
        boolean modifiedChecked = Boolean.TRUE.equals(modifiedNode.getChecked());

        // 处理取消勾选的情况
        if (originalChecked && !modifiedChecked) {
            if (isLeaf(modifiedNode) && NODE_TYPE_RESOURCE.equals(modifiedNode.getValue())) {
                resourceCancel.add(modifiedNode.getId());
            } else {
                menuCancel.add(modifiedNode.getId());
            }
        }

        // 处理新增勾选的情况
        if (!originalChecked && modifiedChecked) {
            if (isLeaf(modifiedNode)) {
                processNewCheckedLeaf(modifiedNode);
            }
        }

        // 递归比较子节点
        List<TreeNode> originalChildren = originalNode.getNodes();
        List<TreeNode> modifiedChildren = modifiedNode.getNodes();
        for (int i = 0; i < modifiedChildren.size(); i++) {
            traverseAndCompare(i < originalChildren.size() ? originalChildren.get(i) : null, modifiedChildren.get(i));
        }
    }

    private boolean isLeaf(TreeNode node) {
        return node.getNodes() == null || node.getNodes().isEmpty();
    }

    private void processNewCheckedLeaf(TreeNode leafNode) {
        if (NODE_TYPE_MENU.equals(leafNode.getValue())) {
            BindAuthorityResourceDto bindAuthorityResourceDto = new BindAuthorityResourceDto();
            bindAuthorityResourceDto.setAuthId(leafNode.getId());
            bindAuthorityResourceDto.setResourceIds(new ArrayList<>());
            authMap.put(leafNode.getId(), bindAuthorityResourceDto);
        } else if (NODE_TYPE_RESOURCE.equals(leafNode.getValue())) {
            TreeNode parent = findNearestMenuParent(leafNode);
            if (parent != null) {
                BindAuthorityResourceDto dto =
                        authMap.computeIfAbsent(parent.getId(), k -> new BindAuthorityResourceDto());
                dto.setAuthId(parent.getId());
                if (dto.getResourceIds() == null) {
                    dto.setResourceIds(new ArrayList<>());
                }
                dto.getResourceIds().add(leafNode.getId());
            }
        } else {
            throw new ServiceException("未知菜单资源节点类型: " + leafNode.getValue());
        }
    }

    private TreeNode findNearestMenuParent(TreeNode node) {
        TreeNode current = node;
        while (current != null) {
            if (NODE_TYPE_MENU.equals(current.getValue())) {
                return current;
            }
            current = modifiedNodeMap.get(current.getPid());
        }
        return null;
    }

    // 数据结构定义
    @Data
    public static class CompareResult {
        private List<String> resourceCancel;
        private List<String> menuCancel;
        private Map<String, BindAuthorityResourceDto> authMap;

        public CompareResult(
                List<String> resourceCancel, List<String> menuCancel, Map<String, BindAuthorityResourceDto> authMap) {
            this.resourceCancel = resourceCancel;
            this.menuCancel = menuCancel;
            this.authMap = authMap;
        }
    }
}
