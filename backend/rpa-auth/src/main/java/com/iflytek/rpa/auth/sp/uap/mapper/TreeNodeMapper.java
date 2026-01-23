package com.iflytek.rpa.auth.sp.uap.mapper;

import com.iflytek.rpa.auth.core.entity.TreeNode;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Component;

/**
 * TreeNode映射器
 * 用于将UAP客户端的TreeNode和core包下的TreeNode互相转换
 *
 * 注意：两个TreeNode类的nodes字段都是递归的（List&lt;TreeNode&gt;），
 * 因此转换时需要递归处理子节点。
 *
 * @author xqcao2
 */
@Component
public class TreeNodeMapper {

    /**
     * 将UAP客户端的TreeNode转换为核心实体TreeNode
     * 递归转换nodes列表
     *
     * @param uapTreeNode UAP客户端的TreeNode
     * @return core包下的TreeNode
     */
    public TreeNode fromUapTreeNode(com.iflytek.sec.uap.client.core.dto.TreeNode uapTreeNode) {
        if (uapTreeNode == null) {
            return null;
        }

        TreeNode treeNode = new TreeNode();
        // 使用BeanUtils复制基本属性
        BeanUtils.copyProperties(uapTreeNode, treeNode);

        // 递归转换nodes列表
        if (uapTreeNode.getNodes() != null && !uapTreeNode.getNodes().isEmpty()) {
            List<TreeNode> nodes = new ArrayList<>();
            for (com.iflytek.sec.uap.client.core.dto.TreeNode uapNode : uapTreeNode.getNodes()) {
                TreeNode node = fromUapTreeNode(uapNode);
                if (node != null) {
                    nodes.add(node);
                }
            }
            treeNode.setNodes(nodes);
        } else {
            treeNode.setNodes(new ArrayList<>());
        }

        return treeNode;
    }

    /**
     * 批量将UAP客户端的TreeNode列表转换为核心实体TreeNode列表
     *
     * @param uapTreeNodes UAP客户端的TreeNode列表
     * @return core包下的TreeNode列表
     */
    public List<TreeNode> fromUapTreeNodes(List<com.iflytek.sec.uap.client.core.dto.TreeNode> uapTreeNodes) {
        if (uapTreeNodes == null || uapTreeNodes.isEmpty()) {
            return Collections.emptyList();
        }

        return uapTreeNodes.stream()
                .map(this::fromUapTreeNode)
                .filter(treeNode -> treeNode != null)
                .collect(Collectors.toList());
    }

    /**
     * 将core包下的TreeNode转换为UAP客户端的TreeNode
     * 递归转换nodes列表
     *
     * @param treeNode core包下的TreeNode
     * @return UAP客户端的TreeNode
     */
    public com.iflytek.sec.uap.client.core.dto.TreeNode toUapTreeNode(TreeNode treeNode) {
        if (treeNode == null) {
            return null;
        }

        com.iflytek.sec.uap.client.core.dto.TreeNode uapTreeNode = new com.iflytek.sec.uap.client.core.dto.TreeNode();
        // 使用BeanUtils复制基本属性
        BeanUtils.copyProperties(treeNode, uapTreeNode);

        // 递归转换nodes列表
        if (treeNode.getNodes() != null && !treeNode.getNodes().isEmpty()) {
            List<com.iflytek.sec.uap.client.core.dto.TreeNode> nodes = new ArrayList<>();
            for (TreeNode node : treeNode.getNodes()) {
                com.iflytek.sec.uap.client.core.dto.TreeNode uapNode = toUapTreeNode(node);
                if (uapNode != null) {
                    nodes.add(uapNode);
                }
            }
            uapTreeNode.setNodes(nodes);
        } else {
            uapTreeNode.setNodes(new ArrayList<>());
        }

        return uapTreeNode;
    }

    /**
     * 批量将core包下的TreeNode列表转换为UAP客户端的TreeNode列表
     *
     * @param treeNodes core包下的TreeNode列表
     * @return UAP客户端的TreeNode列表
     */
    public List<com.iflytek.sec.uap.client.core.dto.TreeNode> toUapTreeNodes(List<TreeNode> treeNodes) {
        if (treeNodes == null || treeNodes.isEmpty()) {
            return Collections.emptyList();
        }

        return treeNodes.stream()
                .map(this::toUapTreeNode)
                .filter(uapTreeNode -> uapTreeNode != null)
                .collect(Collectors.toList());
    }
}
