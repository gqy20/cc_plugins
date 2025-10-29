# 进化生态专家 - 标准化数据接口和结果格式

## 1. 标准化数据输入格式

### 1.1 物种分布和丰度数据格式标准

```json
{
  "species_distribution_data": {
    "metadata": {
      "species_name": "string",
      "taxonomic_classification": {
        "kingdom": "string",
        "phylum": "string",
        "class": "string",
        "order": "string",
        "family": "string",
        "genus": "string",
        "species": "string",
        "authority": "string"
      },
      "data_source": "string",
      "collection_period": {
        "start_date": "YYYY-MM-DD",
        "end_date": "YYYY-MM-DD",
        "seasonal_coverage": "string"
      }
    },
    "distribution_records": [
      {
        "record_id": "string",
        "location": {
          "latitude": "decimal",
          "longitude": "decimal",
          "coordinate_precision": "decimal",
          "elevation": "decimal",
          "habitat_description": "string"
        },
        "abundance_measurements": {
          "abundance_metric": ["count", "density", "biomass", "cover"],
          "value": "decimal",
          "unit": "string",
          "sampling_method": "string",
          "sample_area": "decimal",
          "detection_probability": "decimal"
        },
        "observation_metadata": {
          "observation_date": "YYYY-MM-DD",
          "observer": "string",
          "observation_method": "string",
          "weather_conditions": "string",
          "time_of_day": "string"
        }
      }
    ],
    "environmental_covariates": [
      {
        "variable_name": "string",
        "measurement_value": "decimal",
        "unit": "string",
        "measurement_method": "string",
        "temporal_resolution": "string"
      }
    ]
  }
}
```

### 1.2 生态互作数据格式标准

```json
{
  "species_interaction_data": {
    "metadata": {
      "study_system": "string",
      "focal_species": ["string"],
      "interaction_types": ["predation", "mutualism", "competition", "parasitism", "amensalism"],
      "study_duration": "integer_months",
      "spatial_scale": "string"
    },
    "interaction_network": {
      "nodes": [
        {
          "species_id": "string",
          "species_name": "string",
          "trophic_level": "string",
          "abundance": "decimal",
          "biomass": "decimal",
          "functional_group": "string"
        }
      ],
      "edges": [
        {
          "interaction_id": "string",
          "source_species": "string",
          "target_species": "string",
          "interaction_type": "string",
          "interaction_strength": "decimal",
          "interaction_frequency": "decimal",
          "directionality": "directed|undirected|bidirectional",
          "confidence_score": "decimal",
          "measurement_method": "string"
        }
      ],
      "network_metrics": {
        "connectance": "decimal",
        "modularity": "decimal",
        "nestedness": "decimal",
        "mean_path_length": "decimal",
        "clustering_coefficient": "decimal"
      }
    },
    "temporal_dynamics": [
      {
        "time_point": "YYYY-MM-DD",
        "network_state": "object",
        "environmental_conditions": "object",
        "disturbance_events": ["string"]
      }
    ]
  }
}
```

### 1.3 环境变化数据格式标准

```json
{
  "environmental_change_data": {
    "metadata": {
      "study_region": "string",
      "spatial_extent": {
        "polygon": "GeoJSON",
        "area_km2": "decimal"
      },
      "temporal_extent": {
        "start_year": "integer",
        "end_year": "integer",
        "resolution": "annual|seasonal|monthly"
      }
    },
    "climate_variables": [
      {
        "variable_name": "string",
        "units": "string",
        "time_series": [
          {
            "year": "integer",
            "value": "decimal",
            "anomaly": "decimal",
            "trend": "decimal",
            "statistical_significance": "boolean"
          }
        ],
        "seasonal_patterns": "object",
        "extreme_events": [
          {
            "event_date": "YYYY-MM-DD",
            "event_type": "string",
            "magnitude": "decimal",
            "duration": "integer_days"
          }
        ]
      }
    ],
    "habitat_changes": [
      {
        "habitat_type": "string",
        "baseline_area": "decimal",
        "current_area": "decimal",
        "change_rate": "decimal",
        "fragmentation_metrics": {
          "patch_count": "integer",
          "mean_patch_size": "decimal",
          "edge_density": "decimal",
          "core_area": "decimal"
        },
        "quality_assessment": {
          "vegetation_cover": "decimal",
          "soil_quality": "decimal",
          "hydrological_integrity": "decimal"
        }
      }
    ],
    "anthropogenic_pressures": [
      {
        "pressure_type": ["urbanization", "agriculture", "mining", "forestry", "infrastructure"],
        "intensity": "decimal",
        "spatial_pattern": "object",
        "temporal_trend": "decimal",
        "impact_assessment": "string"
      }
    ]
  }
}
```

## 2. 标准化分析输出格式

### 2.1 适应性景观分析结果格式

```json
{
  "fitness_landscape_analysis": {
    "analysis_metadata": {
      "analysis_date": "YYYY-MM-DDTHH:MM:SSZ",
      "landscape_dimensions": "integer",
      "trait_space": ["string"],
      "method": ["Gaussian_process", "splines", "polynomial", "machine_learning"],
      "data_points": "integer"
    },
    "landscape_properties": {
      "fitness_peaks": [
        {
          "peak_id": "string",
          "location": {
            "trait_values": ["decimal"],
            "fitness_value": "decimal"
          },
          "peak_basin": "object",
          "attraction_strength": "decimal",
          "evolutionary_stability": "stable|unstable|saddle"
        }
      ],
      "fitness_valleys": [
        {
          "valley_id": "string",
          "location": "object",
          "depth": "decimal",
          "width": "decimal",
          "connectivity": "string"
        }
      ],
      "landscape_metrics": {
        "ruggedness_index": "decimal",
        "correlation_length": "decimal",
        "number_of_peaks": "integer",
        "peak_distribution": "string"
      }
    },
    "evolutionary_dynamics": {
      "adaptive_walks": [
        {
          "walk_id": "string",
          "starting_point": "object",
          "ending_point": "object",
          "path_length": "integer",
          "fitness_gained": "decimal",
          "constraint_encountered": "boolean"
        }
      ],
      "evolutionary_predictions": {
        "short_term_evolution": "object",
        "long_term_equilibrium": "object",
        "evolutionary_constraints": ["string"],
        "evolvability_metrics": "object"
      }
    }
  }
}
```

### 2.2 环境响应分析结果格式

```json
{
  "environmental_response_analysis": {
    "response_curves": [
      {
        "trait_name": "string",
        "environmental_variable": "string",
        "functional_response": {
          "response_type": ["linear", "quadratic", "sigmoidal", "threshold", "optimum"],
          "parameters": "object",
          "confidence_intervals": "object",
          "goodness_of_fit": {
            "R_squared": "decimal",
            "AIC": "decimal",
            "BIC": "decimal",
            "log_likelihood": "decimal"
          }
        },
        "critical_thresholds": {
          "optimal_value": "decimal",
          "tolerance_range": {
            "lower": "decimal",
            "upper": "decimal"
          },
          "lethal_thresholds": {
            "lower": "decimal",
            "upper": "decimal"
          }
        },
        "plasticity_metrics": {
          "plasticity_index": "decimal",
          "reaction_norm_slope": "decimal",
          "genetic_correlation": "decimal",
          "environmental_variance": "decimal"
        }
      }
    ],
    "multivariate_responses": {
      "principal_components": [
        {
          "PC_id": "string",
          "explained_variance": "decimal",
          "eigenvalue": "decimal",
          "loadings": "object"
        }
      ],
      "environmental_gradients": [
        {
          "gradient_name": "string",
          "gradient_strength": "decimal",
          "species_responses": "object",
          "community_turnover": "decimal"
        }
      ]
    },
    "temporal_dynamics": {
      "lag_effects": [
        {
          "lag_duration": "integer_days",
          "effect_magnitude": "decimal",
          "confidence_interval": "object"
        }
      ],
      "acclimation_capacity": {
        "acclimation_rate": "decimal",
        "maximum_acclimation": "decimal",
        "acclimation_timeframe": "integer_days"
      }
    }
  }
}
```

### 2.3 专家咨询响应格式

```json
{
  "evolutionary_ecology_consultation": {
    "response_metadata": {
      "consultation_id": "string",
      "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
      "expert_type": "evolutionary_ecology_expert",
      "consultation_type": ["adaptation_analysis", "conservation_strategy", "climate_impact", "community_dynamics"],
      "complexity_level": "basic|intermediate|advanced|expert"
    },
    "ecological_assessment": {
      "system_analysis": {
        "ecosystem_type": "string",
        "key_species": ["string"],
        "trophic_structure": "string",
        "environmental_context": "string"
      },
      "evolutionary_context": {
        "evolutionary_history": "string",
        "selection_regimes": ["string"],
        "genetic_diversity_status": "string",
        "adaptation_potential": "string"
      },
      "threat_assessment": [
        {
          "threat_type": "string",
          "severity": "low|medium|high|critical",
          "timescale": "string",
          "reversibility": "boolean",
          "ecological_consequences": "string"
        }
      ]
    },
    "expert_recommendations": {
      "conservation_strategies": [
        {
          "strategy_name": "string",
          "scientific_rationale": "string",
          "implementation_approach": ["string"],
          "expected_outcomes": "string",
          "success_metrics": ["string"],
          "timeline": "string",
          "cost_estimate": "decimal"
        }
      ],
      "research_priorities": [
        {
          "research_question": "string",
          "methodology": "string",
          "importance_score": "decimal",
          "feasibility": "high|medium|low",
          "potential_impact": "string"
        }
      ],
      "management_actions": [
        {
          "action": "string",
          "urgency": "immediate|short_term|long_term",
          "stakeholder_involvement": ["string"],
          "resource_requirements": "object",
          "monitoring_protocol": "string"
        }
      ]
    },
    "predictions_and_scenarios": {
      "future_scenarios": [
        {
          "scenario_name": "string",
          "assumptions": ["string"],
          "probability": "decimal",
          "time_horizon": "integer_years",
          "projected_outcomes": {
            "species_responses": "object",
            "community_changes": "object",
            "ecosystem_functions": "object"
          }
        }
      ],
      "early_warning_indicators": [
        {
          "indicator_name": "string",
          "threshold_value": "decimal",
          "current_status": "decimal",
          "trend": "improving|stable|declining",
          "monitoring_frequency": "string"
        }
      ]
    }
  }
}
```

## 3. 数据质量标准

### 3.1 生态数据质量评估标准

```json
{
  "ecological_data_quality_assessment": {
    "overall_quality_score": "decimal >= 0.0, <= 1.0",
    "spatial_data_quality": {
      "coordinate_accuracy": "decimal",
      "spatial_coverage": "decimal",
      "sampling_density": "decimal",
      "habitat_representation": "decimal"
    },
    "temporal_data_quality": {
      "time_series_completeness": "decimal",
      "seasonal_coverage": "decimal",
      "temporal_resolution": "string",
      "observation_frequency": "decimal"
    },
    "observation_quality": {
      "observer_expertise": "high|medium|low",
      "identification_certainty": "decimal",
      "detection_probability": "decimal",
      "observation_bias": "decimal"
    },
    "experimental_design_quality": {
      "replication_adequacy": "boolean",
      "randomization_effectiveness": "decimal",
      "control_validity": "boolean",
      "statistical_power": "decimal >= 0.8"
    },
    "data_integrity": {
      "missing_data_percentage": "decimal <= 0.1",
      "outlier_percentage": "decimal <= 0.05",
      "consistency_checks": "passed|warning|failed",
      "validation_status": "validated|partially_validated|unvalidated"
    }
  }
}
```

## 4. 使用指南

### 4.1 数据收集指南
1. 采用标准化的调查方法和协议
2. 确保空间和时间采样的代表性
3. 记录完整的环境背景信息
4. 进行物种鉴定的质量验证

### 4.2 结果解读指南
1. 考虑生态系统的复杂性和非线性特征
2. 评估预测结果的不确定性范围
3. 整合多个证据源进行综合判断
4. 考虑尺度效应对结果的影响

### 4.3 决策支持指南
1. 基于科学证据制定管理策略
2. 考虑社会经济因素的制约
3. 制定适应性管理和监测方案
4. 建立多方参与的决策机制