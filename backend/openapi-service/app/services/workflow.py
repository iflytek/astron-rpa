from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.workflow import Workflow
from app.schemas.workflow import WorkflowBase
from typing import List, Optional
from redis.asyncio import Redis


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
    
    async def create_workflow(self, workflow_data: WorkflowBase, user_id: str) -> Workflow:
        """创建新工作流"""
        # 检查 project_id 是否已存在
        existing_workflow = await self.db.execute(
            select(Workflow).where(Workflow.project_id == workflow_data.project_id)
        )
        if existing_workflow.scalars().first():
            raise ValueError(f"Project ID '{workflow_data.project_id}' already exists")
        
        workflow_dict = workflow_data.model_dump()
        
        workflow = Workflow(
            **workflow_dict,
            user_id=user_id
        )
        
        self.db.add(workflow)
        await self.db.flush()
        await self.db.refresh(workflow)
        
        # 清除缓存
        await self._invalidate_workflows_cache(user_id)
        
        return workflow
    
    async def get_workflow(self, project_id: str, user_id: str = None) -> Optional[Workflow]:
        """获取指定工作流"""
        query = select(Workflow).where(Workflow.project_id == project_id)
        if user_id is not None:
            query = query.where(Workflow.user_id == user_id)
            
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def get_workflows(self, user_id: str = None, skip: int = 0, limit: int = None) -> List[Workflow]:
        """获取工作流列表"""
        # 生成缓存键
        cache_key = f"workflows:{user_id or 'all'}:{skip}:{limit}"
        
        # 如果Redis可用，尝试从缓存获取
        if self.redis:
            cached_data = await self.redis.get(cache_key)
            if cached_data:
                # 这里需要反序列化数据，但不能直接将JSON转为对象
                # 实际中可能需要更复杂的序列化/反序列化方案
                # 由于实现复杂，这里只返回数据库查询结果
                pass
        
        # 构建查询
        if limit is None:
            query = select(Workflow).order_by(Workflow.created_at.desc()).offset(skip)
        else:
            query = select(Workflow).order_by(Workflow.created_at.desc()).offset(skip).limit(limit)

        if user_id is not None:
            query = query.where(Workflow.user_id == user_id)
            
        result = await self.db.execute(query)
        workflows = result.scalars().all()
        
        # 缓存查询结果
        if self.redis:
            # 由于对象序列化复杂，实际项目中可使用专用库或自定义序列化方法
            pass
            
        return workflows
    
    async def update_workflow(self, workflow_data: WorkflowBase, user_id: str) -> Optional[Workflow]:
        """更新工作流"""
        # 检查工作流是否存在且属于当前用户
        project_id = str(workflow_data.project_id)
        workflow = await self.get_workflow(project_id, user_id)
        if not workflow:
            return None
            
        # 仅更新提供的字段
        workflow_dict = workflow_data.model_dump(exclude_unset=True, exclude={'project_id'})
        if not workflow_dict:  # 如果没有提供任何字段，直接返回
            return workflow
            
        # 执行更新
        stmt = update(Workflow).where(
            Workflow.project_id == project_id, 
            Workflow.user_id == user_id
        ).values(**workflow_dict)
        
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
        stmt = delete(Workflow).where(
            Workflow.project_id == project_id, 
            Workflow.user_id == user_id
        )
        
        await self.db.execute(stmt)
        
        # 清除缓存
        await self._invalidate_workflows_cache(user_id)
        
        return True
    
    async def get_workflow_stats(self, user_id: str = None) -> dict:
        """获取工作流统计信息"""
        query = select(Workflow)
        if user_id is not None:
            query = query.where(Workflow.user_id == user_id)
        
        result = await self.db.execute(query)
        workflows = result.scalars().all()
        
        total = len(workflows)
        active = sum(1 for w in workflows if w.status == 1)
        inactive = sum(1 for w in workflows if w.status == 0)
        
        return {
            "total": total,
            "active": active,
            "inactive": inactive
        }
