爬取拉钩的职位信息

会议室预约系统
1. 设计表关系和字段
2. 逻辑：
	1. 显示会议室列表及预定状态（已预订，时间，预定人）查看预定详情  -- 首页
	2. + 预定
		1. 将当前会议室 id 传入， 作为默认选择
		2. 当前用户id 传入，作为默认选择
		3. 选择时间段判断：如果用户提交时间段和已经预定冲突，提示更改
	3. 用户登录可以选择取消预定：
		1. 如何判断会议室预订者是当前用户：
			JS 在会议室加一个用户id属性，判断request.session中存的信息如果一致，显示取消按钮
	4. 时间过了之后，预定自动可用 -- 时间的处理
	5. 删除操作不可以删除他人的。
		1. 编辑会议室的权限不可分配给普通用户。 -- 如果不是自己预定的，不显示编辑和删除按钮
		2. 管理员编辑会议室。普通用户无权限新增会议室。
		3. 

		
引入rbac arya
rbac:
菜单 权限 角色 用户
	
	