# 杂交物种形成专家 - 标准化分析流程模板

## 1. 杂交起源分析标准流程模板

### 1.1 完整分析工作流 (Full Hybrid Origin Analysis)

```yaml
workflow_id: hybrid_origin_complete_analysis
workflow_name: 杂交起源完整分析
version: 1.0
estimated_duration: 45-60分钟
complexity_level: advanced

preconditions:
  - 基因组数据可用 (FASTA/FASTQ格式)
  - 样本信息完整 (物种、地理位置、采样时间)
  - 参考基因组或近缘物种数据
  - 计算资源充足 (内存≥16GB, CPU≥8核)

input_requirements:
  genome_data:
    format: ["FASTA", "FASTQ", "VCF"]
    minimum_coverage: 10x
    sample_count: >=3
    species_information: true

  reference_data:
    outgroup_species: >=1
    phylogenetic_markers: optional
    geographic_coordinates: recommended

quality_thresholds:
  sequence_quality: Q30 >= 85%
  coverage_uniformity: >= 90%
  sample_replicates: >=2 per population

workflow_stages:
  - stage_id: data_preparation
    stage_name: 数据准备和质量控制
    estimated_time: 5-10分钟
    required_inputs: [genome_data, reference_data]
    quality_checks:
      - file_format_validation
      - sequence_quality_assessment
      - coverage_analysis
      - contamination_detection

    external_tools:
      - tool_name: genome_quality_checker
        parameters:
          min_quality: 30
          min_coverage: 10
        timeout: 300

    success_criteria:
      - all_quality_checks_passed: true
      - data_completeness_score: >= 0.8

  - stage_id: phylogenetic_analysis
    stage_name: 系统发育分析
    estimated_time: 10-15分钟
    dependencies: [data_preparation]
    required_inputs: [quality_controlled_genomes]

    analysis_steps:
      - sequence_alignment
      - phylogenetic_tree_construction
      - tree_topology_validation
      - bootstrap_analysis

    external_tools:
      - tool_name: phylogenetic_analyzer
        parameters:
          alignment_method: "MAFFT"
          tree_building_method: "IQ-TREE"
          bootstrap_replicates: 1000
        timeout: 600

  - stage_id: hybrid_signal_detection
    stage_name: 杂交信号检测
    estimated_time: 15-20分钟
    dependencies: [phylogenetic_analysis]
    required_inputs: [phylogenetic_tree, aligned_sequences]

    analysis_methods:
      - ABBA_BABA_test
      - D_statistic_calculation
      - f4_ratio_analysis
      - fd_statistic
      - phylogenetic_network_analysis

    skill_invocations:
      - skill_name: hybrid-origin-analysis
        parameters:
          analysis_methods: ["ABBA_BABA", "D_statistic", "f4_ratio"]
          significance_threshold: 0.05
          bootstrap_iterations: 1000
        execution_options:
          parallel_analysis: true
          intermediate_results: save

  - stage_id: gene_flow_analysis
    stage_name: 基因流分析
    estimated_time: 10-15分钟
    dependencies: [hybrid_signal_detection]
    condition: hybrid_signals_detected

    analysis_approaches:
      - temporal_gene_flow_modeling
      - spatial_gene_flow_patterns
      - migration_rate_estimation
      - admixture_proportion_calculation

    skill_invocations:
      - skill_name: gene-flow-mapping
        parameters:
          temporal_resolution: "fine"
          spatial_analysis: true
          confidence_threshold: 0.7
        execution_options:
          visualization: enabled
          detailed_reporting: true

  - stage_id: mechanism_interpretation
    stage_name: 机制解释和理论框架
    estimated_time: 5-10分钟
    dependencies: [gene_flow_analysis]

    interpretation_framework:
      - speciation_mechanism_identification
      - reproductive_isolation_assessment
      - evolutionary_timeline_reconstruction
      - ecological_context_analysis

    skill_invocations:
      - skill_name: speciation-mechanism-advising
        parameters:
          analysis_depth: "comprehensive"
          theoretical_framework: "integrative"
          evidence_strength_threshold: 0.6
        execution_options:
          expert_consultation: true
          alternative_explanations: include

quality_checkpoints:
  - checkpoint_name: data_quality_gate
    stage: data_preparation
    validation_rules:
      - minimum_coverage: 10x
      - sequence_quality: Q30 >= 85%
      - sample_replication: >=2
    failure_action: stop_with_recommendations

  - checkpoint_name: analysis_validation_gate
    stage: hybrid_signal_detection
    validation_rules:
      - statistical_significance: p < 0.05
      - method_consistency: true
      - result_reproducibility: true
    failure_action: retry_with_alternative_methods

  - checkpoint_name: biological_plausibility_gate
    stage: mechanism_interpretation
    validation_rules:
      - evolutionary_consistency: true
      - ecological_feasibility: true
      - genetic_evidence: strong
    failure_action: expert_review_required

output_deliverables:
  primary_report:
    format: markdown
    sections:
      - executive_summary
      - data_quality_assessment
      - hybrid_signal_analysis
      - gene_flow_dynamics
      - mechanism_interpretation
      - confidence_assessment
      - limitations_and_future_work

  supplementary_materials:
    - phylogenetic_trees: ["newick", "nexus", "svg"]
    - statistical_tables: ["csv", "xlsx"]
    - gene_flow_networks: ["graphml", "svg", "interactive_html"]
    - analysis_logs: ["txt", "json"]

  visualization_assets:
    - phylogenetic_tree: high_resolution_svg
    - gene_flow_map: interactive_html
    - temporal_dynamics: animated_timeline
    - statistical_summary: comprehensive_dashboard

expert_validation:
  automated_checks:
    - result_consistency: true
    - statistical_validity: true
    - biological_plausibility: true

  expert_review_criteria:
    - theoretical_soundness: "strong|moderate|weak"
    - evidence_sufficiency: "sufficient|partial|insufficient"
    - conclusion_confidence: "high|medium|low"
    - recommendation_strength: "strong|moderate|weak"
```

### 1.2 快速杂交筛查流程模板 (Quick Hybrid Screening)

```yaml
workflow_id: hybrid_origin_quick_screening
workflow_name: 快速杂交筛查
version: 1.0
estimated_duration: 15-20分钟
complexity_level: intermediate

target_users:
  - 初步研究探索
  - 数据质量评估
  - 研究可行性判断
  - 预算和资源规划

input_requirements:
  minimal_data:
    - sample_sequences: >=2 species
    - basic_species_info: true
    - rough_geographic_info: recommended

  optional_enhancements:
    - additional_reference_species
    - detailed_sample_metadata
    - environmental_context

workflow_stages:
  - stage_id: rapid_assessment
    stage_name: 快速数据评估
    estimated_time: 2-3分钟

    quick_checks:
      - file_format_validation
      - basic_sequence_quality
      - species_identification
      - data_completeness

    external_tools:
      - tool_name: quick_quality_assessor
        timeout: 120

  - stage_id: preliminary_analysis
    stage_name: 初步杂交分析
    estimated_time: 8-12分钟
    dependencies: [rapid_assessment]

    simplified_methods:
      - basic_distance_analysis
      - simple_tree_construction
      - preliminary_D_statistic

    skill_invocations:
      - skill_name: hybrid-origin-analysis
        parameters:
          analysis_depth: "preliminary"
          methods: ["distance_based", "basic_D_statistic"]
          significance_threshold: 0.1
        execution_options:
          fast_mode: true
          limited_visualization: true

  - stage_id: feasibility_assessment
    stage_name: 可行性评估
    estimated_time: 3-5分钟
    dependencies: [preliminary_analysis]

    assessment_criteria:
      - hybrid_evidence_strength
      - data_sufficiency
      - analysis_complexity
      - resource_requirements

    skill_invocations:
      - skill_name: speciation-mechanism-advising
        parameters:
          analysis_type: "feasibility"
          resource_assessment: true
          recommendation_level: "preliminary"

output_deliverables:
  screening_report:
    format: concise_markdown
    sections:
      - data_suitability_summary
      - preliminary_hybrid_evidence
      - feasibility_recommendation
      - resource_requirements
      - next_steps_suggestions

  decision_support:
    - go_no_go_recommendation: boolean
    - confidence_level: decimal
    - additional_data_needed: list
    - estimated_full_analysis_cost: decimal
```

## 2. 研究方案设计标准流程模板

### 2.1 杂交物种形成研究设计模板

```yaml
workflow_id: hybrid_speciation_research_design
workflow_name: 杂交物种形成研究方案设计
version: 1.0
estimated_duration: 30-40分钟
complexity_level: expert

design_phases:
  - phase_id: problem_definition
    phase_name: 研究问题定义和目标设定
    estimated_time: 5-8分钟

    activities:
      - scientific_question_formulation
      - hypothesis_development
      - objective_prioritization
      - success_criteria_definition

    external_tools:
      - tool_name: literature_synthesizer
        parameters:
          search_depth: "comprehensive"
          timeframe: "last_10_years"
        timeout: 300

  - phase_id: theoretical_framework
    phase_name: 理论框架选择
    estimated_time: 8-10分钟
    dependencies: [problem_definition]

    framework_options:
      - speciation_theories: ["allopatric", "sympatric", "parapatric", "ecological"]
      - hybrid_speciation_models: ["hybrid_stasis", "hybrid_origin", "hybrid_swarm"]
      - analytical_approaches: ["genomic", "ecological", "experimental", "comparative"]

    skill_invocations:
      - skill_name: speciation-mechanism-advising
        parameters:
          framework_depth: "comprehensive"
          multiple_hypotheses: true
          theoretical_rigor: "high"
        execution_options:
          alternative_frameworks: include
          feasibility_analysis: true

  - phase_id: methodological_design
    phase_name: 方法学设计
    estimated_time: 10-12分钟
    dependencies: [theoretical_framework]

    design_components:
      - sampling_strategy
      - data_collection_protocols
      - analytical_methods
      - validation_approaches

    skill_invocations:
      - skill_name: hybrid-origin-analysis
        parameters:
          design_focus: "methodology"
          sampling_optimization: true
          cost_effectiveness: "high"
        execution_options:
          detailed_protocols: true
          quality_controls: include

  - phase_id: resource_planning
    phase_name: 资源规划和预算制定
    estimated_time: 5-8分钟
    dependencies: [methodological_design]

    planning_elements:
      - personnel_requirements
      - equipment_needs
      - timeline_development
      - risk_assessment
      - budget_estimation

  - phase_id: integration_and_optimization
    phase_name: 方案整合和优化
    estimated_time: 2-4分钟
    dependencies: [resource_planning]

    optimization_criteria:
      - scientific_rigor
      - feasibility
      - cost_effectiveness
      - timeline_realism
      - success_probability

deliverables:
  comprehensive_research_plan:
    sections:
      - executive_summary
      - research_background_and_significance
      - objectives_and_hypotheses
      - theoretical_framework
      - methodology
      - timeline_and_milestones
      - resources_and_budget
      - risk_assessment_and_mitigation
      - expected_outcomes_and_impact

  implementation_checklist:
    - data_collection_protocols
    - quality_control_procedures
    - data_management_plan
    - analysis_workflow
    - reporting_framework

  monitoring_framework:
    - progress_indicators
    - quality_metrics
    - timeline_tracking
    - budget_monitoring
    - risk_management
```

## 3. 专家咨询标准流程模板

### 3.1 综合专家咨询流程模板

```yaml
workflow_id: comprehensive_expert_consultation
workflow_name: 综合专家咨询
version: 1.0
estimated_duration: 20-30分钟
complexity_level: adaptive

consultation_types:
  - type_id: theoretical_inquiry
    type_name: 理论咨询
    estimated_duration: 15-25分钟
    focus_areas:
      - hybrid_speciation_theory
      - evolutionary_mechanisms
      - methodological_approaches
      - case_studies_analysis

  - type_id: data_analysis_guidance
    type_name: 数据分析指导
    estimated_duration: 25-35分钟
    focus_areas:
      - analysis_method_selection
      - result_interpretation
      - troubleshooting
      - validation_strategies

  - type_id: research_strategy_advice
    type_name: 研究策略建议
    estimated_duration: 20-30分钟
    focus_areas:
      - experimental_design
      - sampling_strategies
      - technology_selection
      - timeline_planning

consultation_workflow:
  - stage_id: need_assessment
    stage_name: 需求评估
    estimated_time: 2-3分钟

    assessment_activities:
      - query_classification
      - complexity_evaluation
      - information_gathering
      - expectation_setting

  - stage_id: knowledge_retrieval
    stage_name: 知识检索和分析
    estimated_time: 5-8分钟

    retrieval_activities:
      - expert_knowledge_base_search
      - literature_evidence_gathering
      - case_studies_identification
      - best_practices_extraction

    external_tools:
      - tool_name: knowledge_synthesizer
        parameters:
          search_comprehensiveness: "high"
          evidence_quality_threshold: 0.7
          synthesis_depth: "detailed"
        timeout: 300

  - stage_id: contextual_analysis
    stage_name: 上下文分析
    estimated_time: 3-5分钟
    dependencies: [knowledge_retrieval]

    analysis_dimensions:
      - user_background_assessment
      - application_context_understanding
      - constraint_identification
      - opportunity_recognition

  - stage_id: response_formulation
    stage_name: 响应制定
    estimated_time: 8-12分钟
    dependencies: [contextual_analysis]

    formulation_activities:
      - expert_response_development
      - evidence_integration
      - practical_recommendation_formulation
      - uncertainty_disclosure

    conditional_skill_invocations:
      - skill_name: hybrid-origin-analysis
        condition: "empirical_evidence_needed"
        parameters:
          analysis_depth: "consultation_level"
          case_study_focused: true

      - skill_name: speciation-mechanism-advising
        condition: "mechanistic_explanation_needed"
        parameters:
          explanation_level: "expert_consultation"
          practical_examples: include

  - stage_id: quality_assurance
    stage_name: 质量保证
    estimated_time: 2-3分钟
    dependencies: [response_formulation]

    quality_checks:
      - scientific_accuracy
      - clarity_and_completeness
      - practical_relevance
      - uncertainty_handling

response_standards:
  expert_response_structure:
    executive_summary: "concise_2_3_sentences"
    detailed_explanation: "comprehensive_yet_accessible"
    supporting_evidence: "relevant_and_current"
    practical_recommendations: "actionable_and_specific"
    limitations_disclosure: "transparent_and_honest"
    follow_up_suggestions: "helpful_and_targeted"

  quality_metrics:
    - scientific_accuracy: >= 0.9
    - clarity_score: >= 0.8
    - practical_relevance: >= 0.7
    - completeness_score: >= 0.8
    - user_satisfaction_target: >= 0.8
```

## 4. 使用指南和最佳实践

### 4.1 工作流选择指南

1. **根据研究阶段选择工作流**
   - 探索阶段：快速筛查流程
   - 确证阶段：完整分析流程
   - 设计阶段：研究方案设计流程

2. **根据数据质量选择**
   - 高质量数据：完整分析流程
   - 有限数据：快速筛查 + 专家咨询

3. **根据资源约束选择**
   - 充足资源：完整分析流程
   - 资源有限：分阶段实施

### 4.2 质量保证最佳实践

1. **数据质量优先**
   - 严格的数据验证
   - 明确的质量阈值
   - 透明的质量报告

2. **方法学严谨性**
   - 多方法交叉验证
   - 统计显著性检验
   - 结果可重现性

3. **结果解释谨慎性**
   - 明确不确定性
   - 提供多种解释
   - 建议验证实验

### 4.3 扩展和定制指南

1. **工作流定制**
   - 调整质量阈值
   - 添加特定分析方法
   - 整合领域专业知识

2. **输出格式定制**
   - 调整报告详细程度
   - 添加特定可视化
   - 整合用户需求

3. **性能优化**
   - 并行化计算密集步骤
   - 缓存重复计算结果
   - 优化内存使用