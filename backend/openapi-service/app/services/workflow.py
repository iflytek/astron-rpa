import json
from typing import Optional

import httpx
from redis.asyncio import Redis
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.logger import get_logger
from app.models.workflow import Workflow
from app.schemas.workflow import WorkflowBase

logger = get_logger(__name__)

ASTRON_AGENT_WORKFLOWS_URL = "https://xingchen-api.xf-yun.com/manage/workflow/get_info"


class WorkflowService:
    def __init__(self, db: AsyncSession, redis: Redis = None):
        self.db = db
        self.redis = redis

    async def _invalidate_workflows_cache(self, user_id: str) -> None:
        """清除用户工作流缓存"""
        if self.redis:
            # 清除可能的所有分页缓存
            keys = await self.redis.keys(f"workflows:{user_id}:*")
            if keys:
                await self.redis.delete(*keys)

    async def _compare_and_merge_parameters(
        self, robot_params: Optional[str], existing_params: Optional[str]
    ) -> Optional[str]:
        """
        比较新旧参数并合并

        如果robot_params未设置，则与existing_params进行对比，
        如果id, varDirection, varName, varType, varValue有任何一项不同，就更新那一条记录

        Args:
            robot_params: 新的参数JSON字符串
            existing_params: 现有的参数JSON字符串

        Returns:
            合并后的参数JSON字符串
        """
        logger.info("开始比较和合并工作流参数")

        # 解析现有参数
        try:
            existing_list = json.loads(existing_params)
            robot_params = json.loads(robot_params)
        except (json.JSONDecodeError, TypeError):
            logger.exception("解析现有参数失败")
            return None

        logger.info("现有参数数量: %s", len(existing_list))
        logger.info("新参数数量: %s", len(robot_params))

        # 创建现有参数的id映射便于查询
        existing_params_map = {param.get("id"): param for param in existing_list}

        # 以robot_params为准进行更新
        updated_list = []
        updated_count = 0
        added_count = 0

        for robot_param in robot_params:
            robot_param_id = robot_param.get("id")
            existing_param = existing_params_map.get(robot_param_id)

            if existing_param:
                # 现有参数中存在，检查关键字段是否有变化
                if (
                    existing_param.get("varDirection") != robot_param.get("varDirection")
                    or existing_param.get("varName") != robot_param.get("varName")
                    or existing_param.get("varType") != robot_param.get("varType")
                    or existing_param.get("varValue") != robot_param.get("varValue")
                    or existing_param.get("processId") != robot_param.get("processId")
                    or existing_param.get("varDescribe") != robot_param.get("varDescribe")
                ):
                    # 更新这条记录（保留其他字段）
                    logger.info("参数 %s 检测到变化，进行更新", robot_param_id)

                    # 对于描述字段，如果两个都不为空，用新的描述
                    varDescribe = robot_param.get("varDescribe")
                    if not existing_param.get("varDescribe"):
                        varDescribe = robot_param.get("varDescribe")
                    if not robot_param.get("varDescribe"):
                        varDescribe = existing_param.get("varDescribe")

                    updated_param = existing_param.copy()
                    updated_param.update(
                        {
                            "varDirection": robot_param.get("varDirection"),
                            "varName": robot_param.get("varName"),
                            "varType": robot_param.get("varType"),
                            "varValue": robot_param.get("varValue"),
                            "processId": robot_param.get("processId"),
                            "varDescribe": varDescribe,
                        }
                    )
                    updated_list.append(updated_param)
                    updated_count += 1
                else:
                    # 保持现有参数不变
                    updated_list.append(existing_param)
            else:
                # 现有参数中不存在，这是新参数，直接添加
                logger.info("检测到新参数 %s，直接添加", robot_param_id)
                updated_list.append(robot_param)
                added_count += 1

        # 记录删除的参数
        deleted_count = len(existing_list) - len(
            [p for p in existing_list if p.get("id") in {rp.get("id") for rp in robot_params}]
        )
        if deleted_count > 0:
            logger.info("检测到 %s 个已删除的参数", deleted_count)

        logger.info(
            "参数更新完成 - 更新: %s, 新增: %s, 删除: %s, 最终参数数量: %s",
            updated_count,
            added_count,
            deleted_count,
            len(updated_list),
        )

        # 返回更新后的参数JSON
        return json.dumps(updated_list, ensure_ascii=False)

    async def create_workflow(self, workflow_data: WorkflowBase, user_id: str) -> Workflow:
        """创建新工作流"""
        # 检查 project_id 是否已存在
        existing_workflow = await self.db.execute(
            select(Workflow).where(Workflow.project_id == workflow_data.project_id)
        )
        if existing_workflow.scalars().first():
            raise ValueError(f"Project ID '{workflow_data.project_id}' already exists")

        workflow_dict = workflow_data.model_dump()

        workflow = Workflow(**workflow_dict, user_id=user_id)

        self.db.add(workflow)
        await self.db.flush()
        await self.db.refresh(workflow)

        # 清除缓存
        await self._invalidate_workflows_cache(user_id)

        return workflow

    async def get_workflow(self, project_id: str, user_id: str | None = None) -> Optional[Workflow]:
        """获取指定工作流"""
        query = select(Workflow).where(Workflow.project_id == project_id)
        if user_id is not None:
            query = query.where(Workflow.user_id == user_id)

        result = await self.db.execute(query)
        workflow = result.scalars().first()

        # 如果直接搜没搜到project_id，尝试通过example_project_id查找
        if not workflow and user_id is not None:
            example_query = select(Workflow).where(
                Workflow.user_id == user_id,
                Workflow.example_project_id == project_id,
                Workflow.example_project_id.isnot(None),
            )
            result = await self.db.execute(example_query)
            workflow = result.scalars().first()

        return workflow

    async def get_workflows(
        self, user_id: str | None = None, skip: int = 0, limit: int | None = None
    ) -> list[Workflow]:
        """获取工作流列表（仅返回状态为1的项目）"""
        base_query = select(Workflow).where(Workflow.status == 1)

        if limit is None:
            query = base_query.order_by(Workflow.created_at.desc()).offset(skip)
        else:
            query = base_query.order_by(Workflow.created_at.desc()).offset(skip).limit(limit)
        # 如果指定了用户ID，添加用户过滤条件
        if user_id is not None:
            query = query.where(Workflow.user_id == user_id)
        result = await self.db.execute(query)
        workflows = result.scalars().all()
        return workflows

    async def update_workflow(self, workflow_data: WorkflowBase, user_id: str) -> Optional[Workflow]:
        """更新工作流"""
        # 检查工作流是否存在且属于当前用户
        project_id = str(workflow_data.project_id)
        workflow = await self.get_workflow(project_id, user_id)
        if not workflow:
            return None

        # 仅更新提供的字段
        workflow_dict = workflow_data.model_dump(exclude_unset=True, exclude={"project_id"})
        if not workflow_dict:  # 如果没有提供任何字段，直接返回
            return workflow

        if "parameters" in workflow_dict:
            logger.info(workflow_dict["parameters"])
            # 用户没设置parameters，去请求接口并比较
            merged_params = await self._compare_and_merge_parameters(
                workflow_dict["parameters"],  # 新参数为None表示用户未设置
                workflow.parameters,  # 现有参数
            )
            if merged_params is not None:
                workflow_dict["parameters"] = merged_params

        # 执行更新
        stmt = (
            update(Workflow)
            .where(Workflow.project_id == project_id, Workflow.user_id == user_id)
            .values(**workflow_dict)
        )

        await self.db.execute(stmt)

        # 清除缓存
        await self._invalidate_workflows_cache(user_id)

        # 重新获取更新后的工作流
        await self.db.refresh(workflow)
        return workflow

    async def delete_workflow(self, project_id: str, user_id: str) -> bool:
        """删除工作流"""
        # 检查工作流是否存在且属于当前用户
        workflow = await self.get_workflow(project_id, user_id)
        if not workflow:
            return False

        # 执行删除
        stmt = delete(Workflow).where(Workflow.project_id == project_id, Workflow.user_id == user_id)

        await self.db.execute(stmt)

        # 清除缓存
        await self._invalidate_workflows_cache(user_id)

        return True

    async def get_workflow_stats(self, user_id: str | None = None) -> dict:
        """获取工作流统计信息"""
        query = select(Workflow)
        if user_id is not None:
            query = query.where(Workflow.user_id == user_id)

        result = await self.db.execute(query)
        workflows = result.scalars().all()

        total = len(workflows)
        active = sum(1 for w in workflows if w.status == 1)
        inactive = sum(1 for w in workflows if w.status == 0)

        return {"total": total, "active": active, "inactive": inactive}

    async def get_astron_workflows(self, auth_id: int, app_id: str, api_key: str, api_secret: str):
        """获取星辰Agent所有工作流"""
        try:
            headers = {
                "X-Consumer-Username": app_id,
                "Authorization": f"Bearer {api_key}:{api_secret}",
                "Content-Type": "application/json",
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(ASTRON_AGENT_WORKFLOWS_URL, headers=headers)
                response.raise_for_status()

                result = response.json()

                # 检查API响应是否成功
                if result.get("code") != 0:
                    logger.error("Astron API error: %s", result.get("message", "Unknown error"))
                    return []

                # 提取工作流数据
                workflows_data = result.get("data", {})
                workflows = workflows_data.get("pageData", [])

                # 格式化返回数据，只保留关键信息
                formatted_workflows = []
                for workflow in workflows:
                    formatted_workflows.append(
                        {
                            "authId": auth_id,
                            "flowId": workflow.get("flowId"),
                            "name": workflow.get("name"),
                            "description": workflow.get("description", ""),
                            "inputs": workflow.get("ioParams", {}).get("inputs", []),
                            "outputs": workflow.get("ioParams", {}).get("outputs", []),
                            "createTime": workflow.get("createTime"),
                            "updateTime": workflow.get("updateTime"),
                        }
                    )

                return formatted_workflows

        except httpx.TimeoutException:
            logger.error("Timeout when calling Astron API for app_id: %s", app_id)
            return []
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error when calling Astron API for app_id %s: %s", app_id, str(e))
            return []
        except Exception as e:
            logger.error("Error calling Astron API for app_id %s: %s", app_id, str(e))
            return []
