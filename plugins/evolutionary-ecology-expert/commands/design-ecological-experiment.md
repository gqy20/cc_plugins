# 生态学实验设计命令

## 命令功能
由进化生态学专家为您设计科学、严谨的生态学实验，从假设提出到数据分析提供全流程的实验设计指导。

## 使用方法
```bash
/design-ecological-experiment <研究问题> [实验系统] [约束条件]
```

## 参数说明
- `研究问题`：您想解决的科学问题
- `实验系统`：可选，目标实验系统或物种
- `约束条件**：可选，预算、时间、场地等限制

## 设计内容

### 科学问题凝练
专家会帮助您凝练和优化研究问题：
- **问题重要性评估**：理论和实践价值分析
- **可检验性分析**：假设是否可被实验验证
- **创新性评价**：相对于现有研究的创新点
- **可行性评估**：技术、资源、时间可行性

### 假设构建与预测
基于理论构建可检验的科学假设：
- **理论背景梳理**：相关理论和实证研究综述
- **假设框架建立**：主要假设和子假设体系
- **预测制定**：基于假设的具体预测
- **可证伪性设计**：确保假设具有可证伪性

### 实验方案设计
设计完整的实验实施方案：
1. **实验系统选择**
   - 模式生物vs非模式生物
   - 实验室vs野外实验
   - 单物种vs群落实验
   - 短期vs长期实验

2. **处理设计**
   - 处理因子和水平
   - 对照组设置
   - 随机化方法
   - 重复设计

3. **观测指标**
   - 主要响应变量
   - 次要响应变量
   - 测量方法
   - 采样频率

4. **环境控制**
   - 环境因子控制
   - 干扰因素排除
   - 环境监测
   - 数据质量控制

## 实验设计方法

### 1. 假设驱动设计
```python
def hypothesis_driven_design(research_question, theoretical_background):
    """假设驱动的实验设计"""

    # 1. 假设构建
    primary_hypothesis = formulate_primary_hypothesis(research_question, theoretical_background)
    alternative_hypotheses = generate_alternative_hypotheses(primary_hypothesis)

    # 2. 预测制定
    specific_predictions = derive_specific_predictions(primary_hypothesis)
    testable_outcomes = define_testable_outcomes(specific_predictions)

    # 3. 实验设计
    experimental_treatments = design_experimental_treatments(testable_outcomes)
    measurement_protocols = develop_measurement_protocols(experimental_treatments)

    # 4. 统计分析设计
    statistical_tests = select_statistical_tests(experimental_treatments)
    power_analysis = perform_power_analysis(statistical_tests)

    return hypothesis_driven_experiment_plan
```

### 2. 系统性实验设计
```python
def systematic_experiment_design(research_objectives, constraints):
    """系统性实验设计"""

    # 1. 因素设计
    experimental_factors = identify_experimental_factors(research_objectives)
    factor_levels = determine_factor_levels(experimental_factors)
    design_structure = select_design_structure(factor_levels)

    # 2. 随机化设计
    randomization_scheme = develop_randomization_scheme(design_structure)
    blocking_strategy = design_blocking_strategy(randomization_scheme)

    # 3. 重复设计
    replication_levels = determine_replication_levels(design_structure, constraints)
    sample_size_calculation = calculate_sample_size(replication_levels)

    # 4. 时间设计
    temporal_design = design_temporal_structure(research_objectives)
    sampling_schedule = develop_sampling_schedule(temporal_design)

    return systematic_experiment_design_plan
```

### 3. 多尺度实验设计
```python
def multi_scale_experiment_design(scales_of_interest):
    """多尺度实验设计"""

    # 1. 尺度整合
    scale_integration = integrate_multiple_scales(scales_of_interest)
    cross_scale_links = identify_cross_scale_links(scale_integration)

    # 2. 层次设计
    hierarchical_design = design_hierarchical_experiment(scale_integration)
    nested_structures = design_nested_structures(hierarchical_design)

    # 3. 协调设计
    coordination_mechanisms = design_coordination_mechanisms(nested_structures)
    data_integration = plan_data_integration(coordination_mechanisms)

    # 4. 尺度推断
    scaling_methods = select_scaling_methods(data_integration)
    cross_scale_validation = design_cross_scale_validation(scaling_methods)

    return multi_scale_experiment_plan
```

## 示例
```bash
# 设计捕食者-猎物实验
/design-ecological-experiment 捕食者如何影响猎物种群动态 昆虫系统 实验室条件

# 设计植物竞争实验
/design-ecological-experiment 资源竞争对植物群落结构的影响 草地生态系统 长期监测

# 设计行为选择实验
/design-ecological-experiment 鸟类觅食行为的自然选择 鸟类系统 野外观察
```

## 输出内容
- **研究问题优化报告**
- **假设与预测体系**
- **详细实验设计方案**
- **观测指标和测量协议**
- **统计分析计划**
- **风险评估和应急预案**
- **预算和时间表**

## 专家设计特色

### 严谨性保证
- **理论基础**：基于坚实的生态学和进化论理论
- **逻辑严密**：假设-预测-检验的逻辑链条
- **统计严格**：严格的统计设计和分析
- **对照设置**：科学的对照组和重复设计

### 创新性设计
- **思路创新**：突破传统实验设计思路
- **方法创新**：采用新的实验技术和方法
- **尺度创新**：多尺度、多层次的实验整合
- **技术整合**：多种技术的协同应用

### 可行性导向
- **资源约束**：充分考虑资源和技术限制
- **时间规划**：合理的时间安排和里程碑
- **风险评估**：识别和规避潜在风险
- **灵活性**：设计具有一定的调整空间

## 典型实验设计案例

### 1. 捕食者-猎物动态实验
**科学问题**：捕食者密度如何影响猎物种群波动？
**设计特色**：
- 多梯度捕食者密度设计
- 微宇宙系统控制环境变量
- 高频次种群监测
- 数学模型拟合和验证

### 2. 植物竞争实验
**科学问题**：资源异质性如何影响植物竞争格局？
**设计特色**：
- 资源梯度控制实验
- 根系观测窗技术
- 长期群落动态监测
- 资源利用效率分析

### 3. 行为选择实验
**科学问题**：鸟类觅食行为的适应性意义？
**设计特色**：
- 野外行为观察
- 食物资源操纵实验
- 适合度关联分析
- 遗传基础分析

## 实验实施支持

### 技术支持
- **设备选择**：推荐合适的实验设备
- **技术培训**：提供必要的技术培训
- **方法优化**：优化实验方法和技术
- **质量控制**：建立质量控制体系

### 数据分析支持
- **数据管理**：设计数据管理和存储系统
- **统计分析**：提供统计分析指导
- **结果解释**：协助结果解释和讨论
- **论文写作**：指导论文写作和发表

### 问题解决支持
- **实验调整**：根据实际情况调整实验方案
- **问题诊断**：诊断实验中的技术问题
- **应急处理**：提供应急处理方案
- **经验分享**：分享相关实验经验

## 质量保证体系
- **科学标准**：遵循国际生态学实验标准
- **伦理规范**：符合实验伦理和动物福利要求
- **安全规范**：确保实验安全和环境保护
- **可重现性**：实验设计确保结果可重现

选择我的生态学实验设计服务，您将获得最专业、最严谨、最创新的实验设计方案，为您的研究成功提供坚实保障。