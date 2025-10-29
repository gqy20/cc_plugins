# 进化生态专家 - 标准化分析流程模板

## 1. 物种适应性分析流程模板

### 1.1 完整适应性分析 (Complete Adaptation Analysis)

```yaml
workflow_id: complete_adaptation_analysis
workflow_name: 物种完整适应性分析
version: 1.0
estimated_duration: 60-90分钟
complexity_level: advanced

preconditions:
  - 物种分布数据充足 (≥50个记录点)
  - 环境变量数据完整
  - 时间序列数据可用 (≥5年)
  - 多个种群或环境梯度覆盖

input_requirements:
  species_distribution_data:
    observation_records: "≥50_valid_records"
    geographic_coverage: "representative_of_range"
    temporal_coverage: "≥5_years_or_seasonal"
    abundance_data: "recommended"
    detection_probability: "characterized"

  environmental_data:
    climate_variables: ["temperature", "precipitation", "humidity"]
    habitat_variables: ["vegetation", "soil_type", "elevation"]
    anthropogenic_factors: ["land_use", "pollution", "disturbance"]
    temporal_resolution: "monthly_or_seasonal"
    spatial_resolution: "appropriate_for_scale"

  phenotypic_data:
    trait_measurements: "multiple_functional_traits"
    genetic_diversity: "neutral_markers"
    fitness_components: "survival, reproduction, growth"
    plasticity_measurements: "common_garden_or_reciprocal_transplant"

quality_thresholds:
  spatial_representation: ≥0.8
  temporal_coverage: ≥0.7
  detection_probability: ≥0.6
  sample_size_per_environment: ≥10

workflow_stages:
  - stage_id: data_integration
    stage_name: 数据整合和质量控制
    estimated_time: 10-15分钟
    required_inputs: [species_distribution_data, environmental_data]

    integration_activities:
      - coordinate_system_standardization
      - temporal_alignment
      - data_quality_assessment
      - missing_data_imputation
      - outlier_detection

    external_tools:
      - tool_name: ecological_data_integrator
        parameters:
          spatial_resolution: "1km"
          temporal_resolution: "monthly"
          quality_threshold: 0.7
        timeout: 600

    skill_invocations:
      - skill_name: natural-selection-analysis
        parameters:
          analysis_type: "data_preparation"
          quality_assessment: "comprehensive"
        execution_options:
          detailed_reporting: true

  - stage_id: environmental_characterization
    stage_name: 环境特征化
    estimated_time: 12-18分钟
    dependencies: [data_integration]

    environmental_analyses:
      - principal_component_analysis
      - environmental_gradient_identification
      - habitat_classification
      - temporal_pattern_analysis
      - spatial_autocorrelation_assessment

    external_tools:
      - tool_name: environmental_analyzer
        parameters:
          PCA_components: 5
          gradient_methods: ["PCA", "RDA", "CCA"]
          spatial_analysis: "enabled"
        timeout: 900

  - stage_id: adaptation_pattern_analysis
    stage_name: 适应性模式分析
    estimated_time: 15-20分钟
    dependencies: [environmental_characterization]

    adaptation_analyses:
      - trait-environment_relationships
      - local_adaptation_detection
      - plasticity_vs_genetics_disentanglement
      - fitness_landscape_characterization
      - adaptive_evolutionary_potential

    skill_invocations:
      - skill_name: natural-selection-analysis
        parameters:
          analysis_depth: "comprehensive"
          adaptation_focus: "multi_trait"
          statistical_methods: ["GLM", "mixed_effects", "phylogenetic"]
        execution_options:
          model_comparison: true
          uncertainty_quantification: true

  - stage_id: evolutionary_potential_assessment
    stage_name: 进化潜力评估
    estimated_time: 10-15分钟
    dependencies: [adaptation_pattern_analysis]

    evolutionary_assessments:
      - genetic_diversity_analysis
      - effective_population_size
      - gene_flow_patterns
      - evolutionary_constraints
      - adaptive_capacity

    external_tools:
      - tool_name: evolutionary_potential_analyzer
        parameters:
          diversity_metrics: ["heterozygosity", "allelic_richness", "private_alleles"]
          population_structure: "analyze"
          migration_estimation: "enabled"
        timeout: 600

  - stage_id: climate_change_impact
    stage_name: 气候变化影响分析
    estimated_time: 8-12分钟
    dependencies: [evolutionary_potential_assessment]

    climate_analyses:
      - species_distribution_modeling
      - climate_envelope_projection
      - range_shift_prediction
      - extinction_risk_assessment
      - adaptation_capacity_evaluation

    external_tools:
      - tool_name: climate_impact_analyzer
        parameters:
          climate_scenarios: ["RCP4.5", "RCP8.5"]
          time_horizons: [2030, 2050, 2080]
          modeling_approaches: ["MAXENT", "GAM", "BRT"]
        timeout: 800

  - stage_id: conservation_recommendations
    stage_name: 保护建议制定
    estimated_time: 5-10分钟
    dependencies: [climate_change_impact]

    recommendation_framework:
      - conservation_priority_assessment
      - management_strategy_development
      - monitoring_program_design
      - stakeholder_coordination_plan

    skill_invocations:
      - skill_name: adaptive-mechanisms-analysis
        parameters:
          conservation_focus: true
          management_relevance: "high"
          practical_applications: "detailed"
        execution_options:
          action_oriented: true
          stakeholder_friendly: true

quality_checkpoints:
  - checkpoint_name: data_quality_gate
    stage: data_integration
    validation_rules:
      - spatial_representation: ≥0.8
      - temporal_coverage: ≥0.7
      - data_consistency: passed
    failure_action: data_enhancement_recommendations

  - checkpoint_name: statistical_validity_gate
    stage: adaptation_pattern_analysis
    validation_rules:
      - model_assumptions: met
      - statistical_power: ≥0.8
      - effect_sizes: meaningful
    failure_action: method_refinement

  - checkpoint_name: biological_plausibility_gate
    stage: evolutionary_potential_assessment
    validation_rules:
      - genetic_patterns: consistent
      - ecological_realism: plausible
      - evolutionary_logic: sound
    failure_action: expert_review_required

output_deliverables:
  comprehensive_report:
    format: detailed_markdown
    sections:
      - executive_summary
      - data_quality_assessment
      - environmental_characterization
      - adaptation_patterns
      - evolutionary_potential
      - climate_change_vulnerability
      - conservation_recommendations
      - monitoring_framework

  analytical_results:
    - environmental_gradients: ["CSV", "JSON"]
    - trait_environment_relationships: ["CSV", "RDS"]
    - genetic_diversity_metrics: ["CSV", "JSON"]
    - climate_projections: ["GeoJSON", "shapefile"]
    - risk_assessments: ["CSV", "JSON"]

  visualization_assets:
    - species_distribution_maps: ["interactive_HTML", "shapefile"]
    - environmental_gradient_plots: ["SVG", "PNG"]
    - adaptation_landscapes: ["3D_visualization"]
    - climate_impact_scenarios: ["animated_maps"]

expert_validation:
  automated_checks:
    - statistical_validity: assumptions_verified
    - ecological_realism: patterns_plausible
    - conservation_feasibility: practical_constraints_respected

  expert_review_criteria:
    - scientific_rigor: "excellent|good|acceptable|needs_improvement"
    - conservation_value: "critical|high|medium|low"
    - urgency_level: "immediate|short_term|medium_term|long_term"
    - implementation_feasibility: "high|medium|low"
```

### 1.2 快速适应性评估流程模板 (Quick Adaptation Assessment)

```yaml
workflow_id: quick_adaptation_assessment
workflow_name: 快速适应性评估
version: 1.0
estimated_duration: 20-30分钟
complexity_level: intermediate

target_scenarios:
  - 初步保护优先级评估
  - 快速气候脆弱性筛查
  - 研究方向确定
  - 管理决策支持

minimal_requirements:
  distribution_data:
    observation_records: "≥20_points"
    geographic_coverage: "partial_but_representative"
    basic_abundance: "optional"

  environmental_data:
    key_variables: ["temperature", "precipitation"]
    temporal_coverage: "recent_data"
    spatial_resolution: "coarse_acceptable"

workflow_stages:
  - stage_id: rapid_data_assessment
    stage_name: 快速数据评估
    estimated_time: 3-5分钟

    quick_checks:
      - data_availability
      - basic_quality_metrics
      - coverage_assessment
      - preliminary_patterns

  - stage_id: simplified_analysis
    stage_name: 简化分析
    estimated_time: 10-15分钟
    dependencies: [rapid_data_assessment]

    simplified_methods:
      - basic environmental_characterization
      - simple distribution_modeling
      - preliminary_vulnerability_assessment
      - rough_adaptation_capacity

    external_tools:
      - tool_name: rapid_ecological_analyzer
        parameters:
          analysis_depth: "preliminary"
          computational_effort: "optimized"
          key_variables_only: true
        timeout: 600

  - stage_id: quick_recommendations
    stage_name: 快速建议
    estimated_time: 5-8分钟
    dependencies: [simplified_analysis]

    recommendation_focus:
      - conservation_priority_level
      - immediate_threats
      - monitoring_priorities
      - research_needs

    skill_invocations:
      - skill_name: adaptive-mechanisms-analysis
        parameters:
          analysis_type: "quick_assessment"
          priority_focus: "conservation"
          practical_orientation: true
        execution_options:
          concise_reporting: true
          action_oriented: true

output_deliverables:
  assessment_report:
    format: concise_markdown
    sections:
      - data_suitability_summary
      - preliminary_vulnerability_assessment
      - conservation_priority_recommendation
      - immediate_actions_suggested
      - monitoring_priorities

  decision_support:
    - priority_level: "high|medium|low"
    - urgency: "immediate|short_term|medium_term"
    - confidence_level: decimal (0-1)
    - resource_requirements: estimate
    - key_uncertainties: list
```

## 2. 群落生态分析流程模板

### 2.1 完整群落生态分析模板

```yaml
workflow_id: complete_community_ecology_analysis
workflow_name: 完整群落生态分析
version: 1.0
estimated_duration: 75-120分钟
complexity_level: expert

preconditions:
  - 物种名录完整 (≥20个物种)
  - 多样性数据可用
  - 环境梯度存在
  - 时间序列数据 (≥3年)

input_requirements:
  community_data:
    species_list: "comprehensive_taxonomic_inventory"
    abundance_data: "quantitative_abundance_measures"
    functional_groups: "categorized_species"
    trophic_levels: "characterized_food_web"
    spatial_replication: "multiple_sites"

  interaction_data:
    interaction_types: ["predation", "mutualism", "competition", "parasitism"]
    interaction_strength: "quantified_or_estimated"
    observation_frequency: "sufficient_for_analysis"
    network_completeness: "≥70%_of_interactions"

  environmental_context:
    habitat_characteristics: "detailed_habitat_classification"
    environmental_gradients: "measured_and_characterized"
    disturbance_regime: "characterized_disturbance_patterns"
    spatial_structure: "patch_configuration_analyzed"

quality_thresholds:
    sampling_replication: ≥3 sites
    temporal_replication: ≥2 years
    interaction_detection_probability: ≥0.6
    taxonomic_resolution: species_level

workflow_stages:
  - stage_id: community_characterization
    stage_name: 群落特征化
    estimated_time: 15-20分钟
    required_inputs: [community_data, environmental_context]

    characterization_analyses:
      - species_diversity_indices
      - functional_diversity_assessment
      - phylogenetic_diversity
      - community_composition_analysis
      - dominance_patterns

    external_tools:
      - tool_name: community_diversity_analyzer
        parameters:
          diversity_indices: ["Shannon", "Simpson", "Fisher_alpha"]
          functional_diversity: "trait_based"
          phylogenetic_diversity: "PD", "MPD"
        timeout: 800

    skill_invocations:
      - skill_name: ecological-interactions-analysis
        parameters:
          analysis_type: "community_structure"
          diversity_metrics: "comprehensive"
          spatial_analysis: true
        execution_options:
          detailed_reporting: true

  - stage_id: network_analysis
    stage_name: 网络分析
    estimated_time: 20-25分钟
    dependencies: [community_characterization]

    network_analyses:
      - network_topology_metrics
      - modularity_detection
      - nestedness_analysis
      - keystone_species_identification
      - network_stability_assessment

    external_tools:
      - tool_name: ecological_network_analyzer
        parameters:
          network_types: ["food_web", "mutualism", "competition"]
          network_metrics: ["connectance", "modularity", "nestedness"]
          stability_analysis: "enabled"
        timeout: 1000

  - stage_id: dynamics_analysis
    stage_name: 动态分析
    estimated_time: 15-20分钟
    dependencies: [network_analysis]

    dynamic_analyses:
      - species_turnover_patterns
      - network_stability_dynamics
      - succession_patterns
      - disturbance_response
      - temporal_trend_analysis

    skill_invocations:
      - skill_name: ecological-interactions-analysis
        parameters:
          analysis_type: "temporal_dynamics"
          network_stability: "comprehensive"
          resilience_assessment: true
        execution_options:
          time_series_analysis: true
          scenario_modeling: enabled

  - stage_id: functional_analysis
    stage_name: 功能分析
    estimated_time: 10-15分钟
    dependencies: [dynamics_analysis]

    functional_analyses:
      - ecosystem_functioning_assessment
      - functional_trait_distributions
      - ecosystem_service_evaluation
      - functional_redundancy
      - vulnerability_assessment

    external_tools:
      - tool_name: functional_ecology_analyzer
        parameters:
          functional_groups: "predefined_and_data_driven"
          ecosystem_services: "categorized"
          redundancy_analysis: "enabled"
        timeout: 600

  - stage_id: management_implications
    stage_name: 管理含义分析
    estimated_time: 10-15分钟
    dependencies: [functional_analysis]

    management_analyses:
      - conservation_priority_assessment
      - ecosystem_service_valuation
      - restoration_recommendations
      - monitoring_framework_design

    skill_invocations:
      - skill_name: adaptive-mechanisms-analysis
        parameters:
          management_focus: "ecosystem_level"
          restoration_guidance: "detailed"
          monitoring_protocols: "comprehensive"
        execution_options:
          stakeholder_guidance: true
          implementation_ready: true

output_delvelopables:
  comprehensive_report:
    format: detailed_markdown
    sections:
      - executive_summary
      - community_characterization
      - network_structure_analysis
      - dynamics_and_stability
      - functional_assessment
      - conservation_priorities
      - management_recommendations
      - monitoring_framework

  analytical_results:
    - diversity_indices: ["CSV", "JSON"]
    - network_metrics: ["CSV", "graphml"]
    - functional_analysis: ["CSV", "JSON"]
    - temporal_patterns: ["CSV", "JSON"]

  visualization_assets:
    - network_diagrams: ["interactive_HTML", "vector_graphics"]
    - diversity_trends: ["animated_visualizations"]
    - functional_distributions: ["heat_maps", "3D_plots"]
    - ecosystem_service_maps: ["GIS_layers", "interactive_dashboards"]
```

## 3. 保护生物学咨询流程模板

### 3.1 综合保护生物学咨询模板

```yaml
workflow_id: comprehensive_conservation_biology_consultation
workflow_name: 综合保护生物学咨询
version: 1.0
estimated_duration: 45-60分钟
complexity_level: adaptive

consultation_types:
  - type_id: species_assessment
    type_name: 物种评估咨询
    focus_areas:
      - extinction_risk_assessment
      - conservation_status_evaluation
      - recovery_potential
      - management_priorities

  - type_id: ecosystem_management
    type_name: 生态系统管理咨询
    focus_areas:
      - ecosystem_health_assessment
      - restoration_strategies
      - ecosystem_service_maintenance
      - adaptive_management

  - type_id: climate_adaptation
    type_name: 气候适应咨询
    focus_areas:
      - climate_vulnerability_assessment
      - adaptation_strategies
      - assisted_migration
      - evolutionary_rescue

consultation_workflow:
  - stage_id: problem_definition
    stage_name: 问题定义
    estimated_time: 5-8分钟

    definition_activities:
      - conservation_challenge_identification
      - stakeholder_need_assessment
      - scale_and_scope_definition
      - success_criteria_establishment

  - stage_id: scientific_analysis
    stage_name: 科学分析
    estimated_time: 15-20分钟
    dependencies: [problem_definition]

    scientific_activities:
      - evidence_synthesis
      - risk_assessment
      - feasibility_evaluation
      - opportunity_identification

    external_tools:
      - tool_name: conservation_science_synthesizer
        parameters:
          evidence_depth: "comprehensive"
          risk_assessment_method: "standardized"
          time_scope: "5_years"
        timeout: 900

    skill_invocations:
      - skill_name: adaptive-mechanisms-analysis
        parameters:
          consultation_type: "conservation_biology"
          scientific_rigor: "expert_level"
          practical_application: "high_priority"
        execution_options:
          evidence_based: true
          uncertainty_disclosure: thorough

  - stage_id: solution_development
    stage_name: 解决方案开发
    estimated_time: 15-20分钟
    dependencies: [scientific_analysis]

    solution_activities:
      - strategy_development
      - action_plan_creation
      - resource_allocation
      - stakeholder_coordination
      - monitoring_framework

  - stage_id: expert_validation
    stage_name: 专家验证
    estimated_time: 5-10分钟
    dependencies: [solution_development]

    validation_activities:
      - peer_review_consultation
      - feasibility_validation
      - stakeholder_acceptance
      - ethical_considerations

response_standards:
  consultation_response_structure:
    problem_understanding: "demonstrate_deep_conservation_biology_knowledge"
    scientific_rigor: "evidence-based_decision_making"
    practical_applicability: "realistic_implementation_strategies"
    ethical_considerations: "responsible_conservation_practices"
    stakeholder_inclusivity: "collaborative_approach"

  expertise_domains:
    - conservation_genetics
    - landscape_ecology
    - climate_change_biology
    - restoration_ecology
    - conservation_policy
    - stakeholder_engagement
```

## 4. 使用指南和最佳实践

### 4.1 工作流选择指南

1. **根据保护目标选择**
   - 物种保护：适应性分析 + 物种评估咨询
   - 生态系统保护：群落生态分析 + 生态系统管理咨询
   - 气候适应：气候影响分析 + 气候适应咨询

2. **根据数据完整性选择**
   - 完整数据：完整分析流程
   - 部分数据：快速评估 + 专家咨询
   - 数据不足：数据收集建议

3. **根据保护紧迫性选择**
   - 高紧迫性：快速评估 + 立即行动建议
   - 中等紧迫性：完整分析 + 策略规划
   - 低紧迫性：综合分析 + 长期规划

### 4.2 质量保证最佳实践

1. **生态学严谨性**
   - 充分的时空代表性
   - 适当的统计方法
   - 生态学理论指导
   - 不确定性量化

2. **保护实践导向**
   - 实际可行性考虑
   - 资源约束现实性
   - 利益相关者参与
   - 长期可持续性

3. **伦理责任担当**
   - 物种福利考虑
   - 生态系统完整性
   - 代际公平性
   - 社会正义

### 4.3 创新和优化指南

1. **分析技术创新**
   - 新技术整合（环境DNA, AI, 无人机）
   - 大数据分析方法
   - 多学科整合
   - 实时监测系统

2. **保护策略创新**
   - 适应性管理框架
   - 基于自然的解决方案
   - 社区保护模式
   - 技术增强保护

3. - **决策支持创新**
   - 决策分析工具
   - 情景建模系统
   - 利益权衡框架
   - 影响评估工具