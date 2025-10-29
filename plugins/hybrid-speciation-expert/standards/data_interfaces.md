# 杂交物种形成专家 - 标准化数据接口和结果格式

## 1. 标准化数据输入格式

### 1.1 基因组数据格式标准

```json
{
  "genome_data": {
    "metadata": {
      "species_name": "string",
      "sample_id": "string",
      "collection_date": "YYYY-MM-DD",
      "geographic_location": {
        "latitude": "decimal",
        "longitude": "decimal",
        "altitude": "decimal",
        "location_description": "string"
      },
      "data_type": ["genome", "exome", "transcriptome", "targeted_sequencing"],
      "sequencing_platform": "string",
      "coverage_depth": "decimal",
      "assembly_quality": {
        "N50": "integer",
        "total_length": "integer",
        "GC_content": "decimal",
        "contig_count": "integer"
      }
    },
    "sequences": {
      "format": "FASTA/FASTQ",
      "file_path": "string",
      "encoding": "UTF-8",
      "compression": ["gzip", "bz2", "none"]
    },
    "quality_metrics": {
      "Q30_percentage": "decimal >= 0.0, <= 1.0",
      "mean_coverage": "decimal >= 0.0",
      "duplicate_rate": "decimal >= 0.0, <= 1.0",
      "contamination_rate": "decimal >= 0.0, <= 1.0"
    }
  }
}
```

### 1.2 表型数据格式标准

```json
{
  "phenotype_data": {
    "metadata": {
      "species_name": "string",
      "population_id": "string",
      "measurement_protocol": "string",
      "environmental_conditions": {
        "temperature": "decimal",
        "humidity": "decimal",
        "soil_type": "string",
        "altitude": "decimal"
      }
    },
    "traits": [
      {
        "trait_name": "string",
        "trait_type": ["morphological", "physiological", "behavioral", "life_history"],
        "value": "decimal",
        "unit": "string",
        "measurement_error": "decimal",
        "sample_size": "integer",
        "statistical_significance": "boolean"
      }
    ],
    "environmental_covariates": [
      {
        "variable_name": "string",
        "value": "decimal",
        "unit": "string",
        "measurement_method": "string"
      }
    ]
  }
}
```

### 1.3 地理分布数据格式标准

```json
{
  "distribution_data": {
    "metadata": {
      "species_name": "string",
      "data_source": "string",
      "collection_method": "string",
      "temporal_coverage": {
        "start_year": "integer",
        "end_year": "integer",
        "seasonality": "string"
      }
    },
    "occurrences": [
      {
        "occurrence_id": "string",
        "location": {
          "latitude": "decimal",
          "longitude": "decimal",
          "coordinate_uncertainty": "decimal",
          "georeferencing_protocol": "string"
        },
        "observation_date": "YYYY-MM-DD",
        "observer": "string",
        "sample_count": "integer",
        "habitat_description": "string"
      }
    ],
    "environmental_layers": [
      {
        "layer_name": "string",
        "resolution": "string",
        "source": "string",
        "coverage_area": "GeoJSON_polygon"
      }
    ]
  }
}
```

## 2. 标准化分析输出格式

### 2.1 杂交信号检测结果格式

```json
{
  "hybrid_signal_analysis": {
    "analysis_metadata": {
      "analysis_date": "YYYY-MM-DDTHH:MM:SSZ",
      "analysis_version": "string",
      "software_used": ["string"],
      "parameters": {
        "method": "string",
        "significance_threshold": "decimal",
        "bootstrap_iterations": "integer"
      }
    },
    "hybrid_signals": [
      {
        "signal_type": ["ABBA_BABA", "D_statistic", "f4_ratio", "fd", "phylogenetic_network"],
        "statistic_value": "decimal",
        "p_value": "decimal",
        "confidence_interval": {
          "lower": "decimal",
          "upper": "decimal",
          "confidence_level": "decimal"
        },
        "genomic_regions": [
          {
            "chromosome": "string",
            "start_position": "integer",
            "end_position": "integer",
            "signal_strength": "decimal"
          }
        ],
        "interpretation": "string",
        "evidence_strength": "strong|moderate|weak|none"
      }
    ],
    "overall_assessment": {
      "hybrid_detected": "boolean",
      "confidence_score": "decimal >= 0.0, <= 1.0",
      "hybrid_scenario": {
        "scenario_type": ["allopolyploid", "autopolyploid", "homoploid", "introgression"],
        "parent_species": ["string"],
        "hybrid_age_estimate": "decimal",
        "age_uncertainty": "decimal"
      }
    }
  }
}
```

### 2.2 基因流分析结果格式

```json
{
  "gene_flow_analysis": {
    "analysis_metadata": {
      "analysis_date": "YYYY-MM-DDTHH:MM:SSZ",
      "method": ["TreeMix", "EEMS", "MIGRATE-N", "fastsimcoal2"],
      "demographic_model": "string"
    },
    "gene_flow_events": [
      {
        "event_id": "string",
        "source_population": "string",
        "target_population": "string",
        "direction": "bidirectional|unidirectional",
        "migration_rate": "decimal",
        "time_estimate": "decimal",
        "time_uncertainty": "decimal",
        "confidence_interval": {
          "lower": "decimal",
          "upper": "decimal"
        },
        "genomic_ancestry_proportion": {
          "source_ancestry": "decimal",
          "target_ancestry": "decimal"
        }
      }
    ],
    "temporal_dynamics": {
      "time_points": [
        {
          "time_point": "decimal",
          "migration_matrix": "matrix",
          "effective_population_sizes": "array",
          "divergence_times": "array"
        }
      ],
      "overall_trend": "increasing|decreasing|stable|complex"
    },
    "spatial_patterns": {
      "geographic_distance_matrix": "matrix",
      "isolation_by_distance": {
        "correlation_coefficient": "decimal",
        "p_value": "decimal"
      },
      "barriers_to_gene_flow": [
        {
          "barrier_location": "GeoJSON_line",
          "barrier_strength": "decimal",
          "geographic_features": ["mountain", "river", "urban", "agricultural"]
        }
      ]
    }
  }
}
```

### 2.3 专家咨询响应格式

```json
{
  "expert_consultation": {
    "response_metadata": {
      "consultation_id": "string",
      "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
      "expert_type": "hybrid_speciation_expert",
      "consultation_type": ["theoretical_inquiry", "data_analysis", "research_design"],
      "complexity_level": "basic|intermediate|advanced|expert"
    },
    "question_analysis": {
      "primary_question": "string",
      "question_category": ["theory", "methodology", "case_study", "practical_application"],
      "key_concepts": ["string"],
      "additional_context": "string"
    },
    "expert_response": {
      "executive_summary": "string",
      "detailed_explanation": "string",
      "theoretical_framework": {
        "main_theory": "string",
        "supporting_theories": ["string"],
        "key_assumptions": ["string"],
        "limitations": ["string"]
      },
      "empirical_evidence": [
        {
          "study_citation": {
            "authors": ["string"],
            "year": "integer",
            "title": "string",
            "journal": "string",
            "doi": "string"
          },
          "key_findings": "string",
          "relevance_to_question": "string",
          "evidence_strength": "strong|moderate|weak"
        }
      ],
      "practical_recommendations": [
        {
          "recommendation": "string",
          "rationale": "string",
          "implementation_steps": ["string"],
          "potential_challenges": ["string"],
          "success_criteria": "string"
        }
      ]
    },
    "quality_assessment": {
      "confidence_level": "decimal >= 0.0, <= 1.0",
      "knowledge_completeness": "decimal >= 0.0, <= 1.0",
      "uncertainty_sources": ["string"],
      "additional_information_needed": ["string"],
      "expertise_validation": "validated_by_expert|requires_peer_review|preliminary"
    }
  }
}
```

## 3. 数据质量标准

### 3.1 数据质量评估标准

```json
{
  "data_quality_assessment": {
    "overall_quality_score": "decimal >= 0.0, <= 1.0",
    "quality_dimensions": {
      "completeness": {
        "score": "decimal >= 0.0, <= 1.0",
        "missing_data_percentage": "decimal >= 0.0, <= 1.0",
        "critical_fields_complete": "boolean"
      },
      "accuracy": {
        "score": "decimal >= 0.0, <= 1.0",
        "validation_errors": "integer",
        "consistency_check": "passed|warning|failed"
      },
      "reliability": {
        "score": "decimal >= 0.0, <= 1.0",
        "source_credibility": "high|medium|low",
        "methodology_rigor": "string"
      },
      "timeliness": {
        "score": "decimal >= 0.0, <= 1.0",
        "data_age": "integer_days",
        "currency_status": "current|outdated|historical"
      }
    },
    "quality_flags": [
      {
        "flag_type": ["warning", "error", "info"],
        "message": "string",
        "affected_fields": ["string"],
        "recommended_action": "string"
      }
    ],
    "acceptance_criteria": {
      "meets_minimum_standards": "boolean",
      "recommended_improvements": ["string"],
      "usage_limitations": ["string"]
    }
  }
}
```

## 4. 技能调用接口标准

### 4.1 技能调用请求格式

```json
{
  "skill_invocation": {
    "request_id": "string",
    "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
    "skill_name": "string",
    "invocation_type": ["direct", "conditional", "parallel"],
    "parameters": {
      "input_data": "object",
      "analysis_options": "object",
      "output_preferences": "object"
    },
    "execution_context": {
      "preceding_skills": ["string"],
      "following_skills": ["string"],
      "workflow_stage": "string"
    }
  }
}
```

### 4.2 技能执行结果格式

```json
{
  "skill_execution_result": {
    "execution_metadata": {
      "skill_name": "string",
      "execution_id": "string",
      "start_time": "YYYY-MM-DDTHH:MM:SSZ",
      "end_time": "YYYY-MM-DDTHH:MM:SSZ",
      "execution_duration_ms": "integer",
      "success": "boolean",
      "error_message": "string",
      "warning_messages": ["string"]
    },
    "results": {
      "primary_output": "object",
      "supporting_data": "object",
      "visualizations": [
        {
          "type": ["chart", "graph", "map", "network"],
          "format": ["svg", "png", "html", "json"],
          "data": "object",
          "description": "string"
        }
      ]
    },
    "quality_metrics": {
      "confidence_score": "decimal >= 0.0, <= 1.0",
      "data_quality_impact": "positive|neutral|negative",
      "methodology_appropriateness": "string",
      "limitations": ["string"]
    },
    "next_steps": {
      "recommended_follow_up_skills": ["string"],
      "additional_data_needed": ["string"],
      "validation_requirements": ["string"]
    }
  }
}
```

## 5. 工作流程集成标准

### 5.1 工作流程定义格式

```json
{
  "workflow_definition": {
    "workflow_id": "string",
    "workflow_name": "string",
    "workflow_type": ["consultation", "analysis", "research_design"],
    "version": "string",
    "stages": [
      {
        "stage_id": "string",
        "stage_name": "string",
        "stage_type": ["input_validation", "data_processing", "analysis", "interpretation", "output_generation"],
        "required_inputs": ["string"],
        "expected_outputs": ["string"],
        "skills_to_invoke": [
          {
            "skill_name": "string",
            "invocation_condition": "string",
            "parameters": "object",
            "timeout_seconds": "integer"
          }
        ],
        "external_tools_to_call": [
          {
            "tool_name": "string",
            "parameters": "object",
            "condition": "string"
          }
        ],
        "success_criteria": "string",
        "error_handling": "string"
      }
    ],
    "quality_checkpoints": [
      {
        "checkpoint_name": "string",
        "stage_id": "string",
        "validation_rules": ["string"],
        "failure_action": "stop|continue_with_warning|retry"
      }
    ]
  }
}
```

## 6. 使用指南

### 6.1 数据准备指南
1. 确保所有数据字段符合JSON Schema定义
2. 进行数据质量自检，确保质量分数 >= 0.7
3. 提供完整的元数据信息
4. 验证地理坐标和环境参数的准确性

### 6.2 结果解读指南
1. 关注置信度分数，低置信度结果需要谨慎解读
2. 检查质量警告和限制说明
3. 结合多个证据源进行综合判断
4. 注意时间尺度和空间尺度的适用性

### 6.3 接口使用最佳实践
1. 遵循渐进式数据提交原则
2. 保存完整的执行日志和中间结果
3. 定期验证数据质量和格式兼容性
4. 建立结果验证和交叉检查机制