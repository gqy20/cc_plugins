# 作物育种专家 - 标准化分析流程模板

## 1. 品种基因组选择分析流程模板

### 1.1 完整基因组选择分析 (Complete Genomic Selection)

```yaml
workflow_id: complete_genomic_selection
workflow_name: 完整基因组选择分析
version: 1.0
estimated_duration: 60-90分钟
complexity_level: advanced

preconditions:
  - 基因型数据可用 (SNP array, GBS, 或 WGS)
  - 表型数据完整 (多环境、多重复)
  - 训练群体规模足够 (≥200个体)
  - 验证群体独立 (≥100个体)

input_requirements:
  genotypic_data:
    platforms: ["SNP_array", "GBS", "WGS", "targeted_sequencing"]
    marker_density: "medium_to_high (≥5K markers)"
    missing_data_rate: ≤0.1
    minor_allele_frequency: ≥0.05
    data_format: ["VCF", "PLINK", "HapMap"]

  phenotypic_data:
    traits: "multiple_agronomic_traits"
    environments: "≥2_locations or 2_years"
    replications: "≥2_per_location"
    experimental_design: ["RCBD", "alpha_lattice", "split_plot"]
    measurement_precision: "high"

  reference_data:
    genetic_map: "recommended"
    linkage_disequilibrium_info: "optional"
    pedigree_information: "recommended"
    population_structure: "characterized"

quality_thresholds:
  genotype_call_rate: ≥0.95
  phenotype_heritability: ≥0.2
  marker_quality_score: ≥0.8
  environmental_replication: adequate

workflow_stages:
  - stage_id: data_preparation
    stage_name: 数据准备和质量控制
    estimated_time: 10-15分钟
    required_inputs: [genotypic_data, phenotypic_data]

    quality_assessment:
      - genotype_data_validation
      - phenotype_data_cleaning
      - outlier_detection_and_removal
      - missing_data_pattern_analysis
      - population_structure_assessment

    external_tools:
      - tool_name: breeding_data_validator
        parameters:
          genotype_threshold: 0.95
          phenotype_cleaning: "aggressive"
          outlier_detection: "robust"
        timeout: 600

    skill_invocations:
      - skill_name: breeding-design-analysis
        parameters:
          analysis_type: "data_quality_assessment"
          validation_depth: "comprehensive"
        execution_options:
          detailed_reporting: true

  - stage_id: genomic_analysis
    stage_name: 基因组分析
    estimated_time: 15-20分钟
    dependencies: [data_preparation]

    genomic_analyses:
      - marker_quality_filtering
      - linkage_disequilibrium_calculation
      - population_structure_analysis
      - genetic_diversity_assessment
      - relationship_matrix_construction

    external_tools:
      - tool_name: genomic_analyzer
        parameters:
          LD_threshold: 0.2
          PCA_components: 5
          relationship_method: "realized"
        timeout: 900

  - stage_id: prediction_model_development
    stage_name: 预测模型开发
    estimated_time: 20-25分钟
    dependencies: [genomic_analysis]

    modeling_approaches:
      - GBLUP (Genomic Best Linear Unbiased Prediction)
      - Bayesian_methods (BayesB, BayesCπ)
      - machine_learning (Random Forest, Support Vector)
      - ensemble_methods

    cross_validation:
      - method: "k-fold_cv"
      - folds: 5
      - repetitions: 10
      - metrics: ["prediction_accuracy", "bias", "correlation"]

    external_tools:
      - tool_name: genomic_prediction_engine
        parameters:
          methods: ["GBLUP", "BayesB", "RandomForest"]
          cross_validation: "5-fold"
          optimization: "hyperparameter_tuning"
        timeout: 1200

  - stage_id: selection_recommendation
    stage_name: 选择推荐
    estimated_time: 10-15分钟
    dependencies: [prediction_model_development]

    selection_scenarios:
      - conventional_selection_vs_genomic_selection
      - different_selection_intensities
      - economic_optimization
      - risk_assessment

    skill_invocations:
      - skill_name: breeding-improvement-strategy
        parameters:
          analysis_type: "selection_optimization"
          economic_factors: true
          risk_assessment: "comprehensive"
        execution_options:
          scenario_comparison: true
          detailed_recommendations: true

  - stage_id: implementation_plan
    stage_name: 实施计划制定
    estimated_time: 5-10分钟
    dependencies: [selection_recommendation]

    planning_components:
      - crossing_program_design
      - resource_allocation
      - timeline_development
      - monitoring_framework

    skill_invocations:
      - skill_name: breeding-molecular-consultation
        parameters:
          consultation_type: "implementation_planning"
          practical_focus: true
          resource_optimization: true
        execution_options:
          detailed_protocols: true
          risk_mitigation: include

quality_checkpoints:
  - checkpoint_name: data_quality_gate
    stage: data_preparation
    validation_rules:
      - genotype_call_rate: ≥0.95
      - phenotype_completeness: ≥0.9
      - population_size: ≥200
    failure_action: data_enhancement_recommendations

  - checkpoint_name: model_performance_gate
    stage: prediction_model_development
    validation_rules:
      - prediction_accuracy: ≥0.5
      - model_stability: consistent_across_folds
      - economic_viability: positive_NPV
    failure_action: model_optimization_retry

  - checkpoint_name: practicality_gate
    stage: selection_recommendation
    validation_rules:
      - implementation_feasibility: high
      - cost_benefit_ratio: ≥2.0
      - stakeholder_acceptance: positive
    failure_action: strategy_revision

output_deliverables:
  primary_report:
    format: comprehensive_markdown
    sections:
      - executive_summary
      - data_quality_assessment
      - genomic_analysis_results
      - prediction_model_performance
      - selection_recommendations
      - economic_analysis
      - implementation_plan
      - risk_assessment

  analytical_results:
    - prediction_accuracies: ["CSV", "JSON"]
    - genetic_parameters: ["Excel", "JSON"]
    - selection_candidates: ["CSV", "JSON"]
    - economic_projections: ["Excel", "PDF"]

  visualization_assets:
    - prediction_accuracy_plots: ["SVG", "PNG"]
    - selection_response_curves: ["interactive_HTML"]
    - economic_roi_analysis: ["dashboard"]
    - genetic_diversity_charts: ["SVG"]

expert_validation:
  automated_checks:
    - model_validity: statistical_assumptions_met
    - economic_logic: sound_financial_assumptions
    - breeding_feasibility: practical_constraints_respected

  expert_review_criteria:
    - scientific_rigor: "excellent|good|acceptable|needs_improvement"
    - practical_value: "high|medium|low"
    - innovation_level: "breakthrough|incremental|standard"
    - implementation_risk: "low|medium|high"
```

### 1.2 快速育种评估流程模板 (Quick Breeding Assessment)

```yaml
workflow_id: quick_breeding_assessment
workflow_name: 快速育种评估
version: 1.0
estimated_duration: 20-30分钟
complexity_level: intermediate

target_scenarios:
  - 初步品种评估
  - 快速投资决策
  - 预算规划
  - 研究方向确定

minimal_requirements:
  genotypic_data:
    marker_density: "low_to_medium (≥1K markers)"
    sample_size: "≥50 per population"
    basic_quality: acceptable

  phenotypic_data:
    single_trait: "primary_yield_trait"
    single_environment: "acceptable"
    basic_replication: "≥1"

workflow_stages:
  - stage_id: rapid_data_assessment
    stage_name: 快速数据评估
    estimated_time: 3-5分钟

    quick_checks:
      - data_format_validation
      - basic_quality_metrics
      - sample_size_assessment
      - trait_heritability_estimate

  - stage_id: simplified_analysis
    stage_name: 简化分析
    estimated_time: 10-15分钟
    dependencies: [rapid_data_assessment]

    simplified_methods:
      - basic_genomic_relationships
      - simple_prediction_models
      - rough_economic_assessment
      - preliminary_selection_ranking

    external_tools:
      - tool_name: rapid_breeding_analyzer
        parameters:
          analysis_depth: "preliminary"
          computational_effort: "optimized"
        timeout: 600

  - stage_id: quick_recommendation
    stage_name: 快速推荐
    estimated_time: 5-8分钟
    dependencies: [simplified_analysis]

    recommendation_focus:
      - go_no_go_decision
      - resource_requirements_estimate
      - potential_success_probability
      - key_risk_factors

    skill_invocations:
      - skill_name: breeding-improvement-strategy
        parameters:
          analysis_type: "quick_assessment"
          recommendation_level: "preliminary"
          risk_tolerance: "moderate"
        execution_options:
          concise_reporting: true
          focus_essentials: true

output_deliverables:
  assessment_report:
    format: concise_markdown
    sections:
      - data_suitability_summary
      - preliminary_potential_assessment
      - resource_requirement_estimate
      - go_no_go_recommendation
      - key_risk_factors
      - next_steps_suggestions

  decision_support:
    - recommendation: "proceed|conditional_proceed|stop|gather_more_data"
    - confidence_level: decimal (0-1)
    - estimated_cost_range: [min, max]
    - timeline_estimate: string
    - success_probability: decimal (0-1)
```

## 2. 品种改良策略设计流程模板

### 2.1 综合品种改良策略模板

```yaml
workflow_id: comprehensive_variety_improvement
workflow_name: 综合品种改良策略设计
version: 1.0
estimated_duration: 45-60分钟
complexity_level: expert

strategy_phases:
  - phase_id: situation_analysis
    phase_name: 现状分析
    estimated_time: 8-12分钟

    analysis_components:
      - current_variety_assessment
      - market_demand_analysis
      - competitive_landscape
      - resource_inventory
      - constraint_identification

    external_tools:
      - tool_name: market_analyzer
        parameters:
          market_scope: "regional_to_national"
          competitor_analysis: "comprehensive"
          time_horizon: "5_years"
        timeout: 600

    skill_invocations:
      - skill_name: breeding-improvement-strategy
        parameters:
          analysis_type: "situational_assessment"
          market_focus: true
          competitive_analysis: "detailed"

  - phase_id: objective_setting
    phase_name: 目标设定
    estimated_time: 6-8分钟
    dependencies: [situation_analysis]

    objective_framework:
      - breeding_goals_definition
      - success_criteria_establishment
      - timeline_development
      - resource_allocation_planning

  - phase_id: strategy_development
    phase_name: 策略开发
    estimated_time: 15-20分钟
    dependencies: [objective_setting]

    strategy_components:
      - breeding_methodology_selection
      - crossing_program_design
      - selection_intensity_optimization
      - genetic_diversity_management
      - technology_integration

    skill_invocations:
      - skill_name: breeding-design-analysis
        parameters:
          design_type: "comprehensive_strategy"
          optimization_targets: ["yield", "quality", "stress_tolerance"]
          sustainability_focus: true
        execution_options:
          alternative_strategies: include
          risk_analysis: detailed

  - phase_id: implementation_planning
    phase_name: 实施计划
    estimated_time: 8-12分钟
    dependencies: [strategy_development]

    planning_elements:
      - detailed_timeline
      - resource_requirements
      - milestone_definition
      - monitoring_framework
      - risk_management_plan

    skill_invocations:
      - skill_name: breeding-molecular-consultation
        parameters:
          consultation_type: "implementation_planning"
          practical_details: "comprehensive"
          stakeholder_coordination: true

  - phase_id: economic_feasibility
    phase_name: 经济可行性分析
    estimated_time: 6-8分钟
    dependencies: [implementation_planning]

    economic_analysis:
      - cost_benefit_analysis
      - investment_roi_calculation
      - market_value_estimation
      - break_even_analysis
      - sensitivity_analysis

deliverables:
  comprehensive_strategy_plan:
    sections:
      - executive_summary
      - situation_analysis
      - objectives_and_goals
      - detailed_strategy
      - implementation_plan
      - resource_requirements
      - economic_analysis
      - risk_assessment
      - monitoring_framework

  implementation_guidelines:
    - detailed_procedures
    - quality_standards
    - decision_criteria
    - reporting_templates

  economic_model:
    - cost_structure_analysis
    - revenue_projections
    - roi_calculations
    - sensitivity_analysis
```

## 3. 分子育种咨询流程模板

### 3.1 综合分子育种咨询模板

```yaml
workflow_id: comprehensive_molecular_breeding_consultation
workflow_name: 综合分子育种咨询
version: 1.0
estimated_duration: 30-45分钟
complexity_level: adaptive

consultation_types:
  - type_id: technology_selection
    type_name: 技术选择咨询
    focus_areas:
      - genomic_platform_selection
      - sequencing_strategy
      - data_analysis_pipeline
      - technology_integration

  - type_id: protocol_optimization
    type_name: 协议优化咨询
    focus_areas:
      - sampling_strategy
      - experimental_design
      - quality_control
      - data_management

  - type_id: troubleshooting
    type_name: 问题诊断咨询
    focus_areas:
      - data_quality_issues
      - analysis_problems
      - interpretation_difficulties
      - result_validation

consultation_workflow:
  - stage_id: requirement_assessment
    stage_name: 需求评估
    estimated_time: 3-5分钟

    assessment_activities:
      - user_context_understanding
      - current_capability_assessment
      - goal_identification
      - constraint_recognition

  - stage_id: knowledge_synthesis
    stage_name: 知识综合
    estimated_time: 8-12分钟
    dependencies: [requirement_assessment]

    synthesis_activities:
      - current_best_practices_review
      - technology_landscape_analysis
      - case_studies_identification
      - expert_consensus_gathering

    external_tools:
      - tool_name: molecular_breeding_knowledge_base
        parameters:
          search_depth: "comprehensive"
          recency_filter: "last_5_years"
          technology_focus: "current_best_practices"
        timeout: 600

  - stage_id: solution_development
    stage_name: 解决方案开发
    estimated_time: 12-18分钟
    dependencies: [knowledge_synthesis]

    development_activities:
      - customized_solution_design
      - implementation_protocol_development
      - quality_framework_establishment
      - success_metrics_definition

    skill_invocations:
      - skill_name: breeding-molecular-consultation
        parameters:
          consultation_depth: "expert_level"
          practical_focus: "implementation_ready"
          customization_level: "high"
        execution_options:
          detailed_protocols: true
          step_by_step_guidance: true
          troubleshooting_guide: include

  - stage_id: validation_planning
    stage_name: 验证计划
    estimated_time: 5-8分钟
    dependencies: [solution_development]

    validation_components:
      - pilot_study_design
      - success_criteria_definition
      - monitoring_framework
      - feedback_mechanisms

response_standards:
  consultation_response_structure:
    problem_understanding: "demonstrate_comprehensive_understanding"
    solution_rationale: "scientific_evidence_based"
    implementation_guidance: "step_by_step_detailed"
    quality_assurance: "built_in_validation_framework"
    troubleshooting: "anticipate_common_problems"
    follow_up_support: "ongoing_guidance_available"

  expertise_domains:
    - molecular_marker_technologies
    - genomic_selection_platforms
    - high_throughput_phenotyping
    - bioinformatics_pipelines
    - statistical_genetics
    - breeding_program_management
```

## 4. 使用指南和最佳实践

### 4.1 工作流选择指南

1. **根据育种阶段选择**
   - 品种开发初期：快速评估 + 分子育种咨询
   - 品种改良中期：基因组选择分析
   - 品种优化阶段：综合改良策略

2. **根据数据可用性选择**
   - 完整数据：完整分析流程
   - 部分数据：快速评估 + 专家咨询
   - 数据不足：数据收集建议

3. **根据资源约束选择**
   - 充足资源：完整分析 + 综合策略
   - 有限资源：快速评估 + 分阶段实施

### 4.2 质量保证最佳实践

1. **数据质量优先**
   - 严格的基因型和表型数据验证
   - 明确的质量控制标准
   - 透明的质量报告

2. **统计分析严谨性**
   - 适当的统计模型选择
   - 充分的交叉验证
   - 不确定性量化

3. **实际应用导向**
   - 考虑实施可行性
   - 平衡理想性和实用性
   - 关注经济效益

### 4.3 创新和优化指南

1. **技术整合创新**
   - 传统育种与现代分子技术结合
   - 多组学数据整合分析
   - 人工智能辅助决策

2. **流程优化创新**
   - 并行化计算密集步骤
   - 自动化重复性任务
   - 智能化质量控制

3. **决策支持创新**
   - 实时数据更新机制
   - 动态策略调整
   - 风险预警系统