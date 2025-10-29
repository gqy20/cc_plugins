# 作物育种专家 - 标准化数据接口和结果格式

## 1. 标准化数据输入格式

### 1.1 品种特性数据格式标准

```json
{
  "cultivar_data": {
    "metadata": {
      "cultivar_name": "string",
      "species_name": "string",
      "breeding_institution": "string",
      "release_year": "integer",
      "breeding_program": "string",
      "pedigree": {
        "female_parent": "string",
        "male_parent": "string",
        "ancestral_lines": ["string"]
      }
    },
    "genetic_characteristics": {
      "genotype": {
        "marker_data": {
          "platform": ["SNP_array", "GBS", "WGS", "targeted_sequencing"],
          "marker_count": "integer",
          "polymorphic_markers": "integer",
          "missing_data_rate": "decimal <= 0.1"
        },
        "molecular_markers": [
          {
            "marker_id": "string",
            "chromosome": "string",
            "position": "integer",
            "allele1": "string",
            "allele2": "string",
            "quality_score": "decimal"
          }
        ]
      },
      "heritability_estimates": {
        "trait_name": "string",
        "broad_sense_h2": "decimal >= 0.0, <= 1.0",
        "narrow_sense_h2": "decimal >= 0.0, <= 1.0",
        "standard_error": "decimal",
        "confidence_interval": {
          "lower": "decimal",
          "upper": "decimal"
        }
      }
    },
    "phenotypic_characteristics": {
      "agronomic_traits": [
        {
          "trait_name": "string",
          "trait_category": ["yield", "quality", "stress_tolerance", "disease_resistance"],
          "measurement_unit": "string",
          "mean_value": "decimal",
          "standard_deviation": "decimal",
          "sample_size": "integer",
          "environmental_interactions": {
            "GxE_significance": "boolean",
            "stability_index": "decimal",
            "adaptation_range": "string"
          }
        }
      ],
      "quality_traits": [
        {
          "trait_name": "string",
          "industry_standard": "string",
          "measurement_protocol": "string",
          "value": "decimal",
          "grade": "string",
          "market_acceptance": "boolean"
        }
      ]
    }
  }
}
```

### 1.2 育种环境数据格式标准

```json
{
  "breeding_environment": {
    "trial_metadata": {
      "trial_id": "string",
      "location": {
        "site_name": "string",
        "latitude": "decimal",
        "longitude": "decimal",
        "altitude": "decimal",
        "soil_type": "string",
        "climate_zone": "string"
      },
      "trial_design": {
        "design_type": ["RCBD", "alpha_lattice", "split_plot", "augmented"],
        "replications": "integer",
        "block_size": "integer",
        "plot_size": "decimal",
        "border_rows": "integer"
      },
      "planting_conditions": {
        "planting_date": "YYYY-MM-DD",
        "harvest_date": "YYYY-MM-DD",
        "planting_density": "decimal",
        "fertilizer_regime": "string",
        "irrigation_schedule": "string"
      }
    },
    "environmental_measurements": {
      "weather_data": [
        {
          "date": "YYYY-MM-DD",
          "temperature_max": "decimal",
          "temperature_min": "decimal",
          "precipitation": "decimal",
          "humidity": "decimal",
          "solar_radiation": "decimal",
          "wind_speed": "decimal"
        }
      ],
      "soil_measurements": [
        {
          "depth_layer": "string",
          "ph": "decimal",
          "organic_matter": "decimal",
          "nitrogen": "decimal",
          "phosphorus": "decimal",
          "potassium": "decimal",
          "soil_moisture": "decimal"
        }
      ]
    }
  }
}
```

### 1.3 市场需求数据格式标准

```json
{
  "market_demand_data": {
    "market_analysis": {
      "target_market": {
        "region": "string",
        "market_size": "decimal",
        "growth_rate": "decimal",
        "consumer_preferences": ["string"]
      },
      "product_specifications": {
        "quality_requirements": [
          {
            "trait_name": "string",
            "minimum_standard": "decimal",
            "premium_threshold": "decimal",
            "testing_method": "string"
          }
        ],
        "industry_certifications": ["string"],
        "shelf_life_requirements": "decimal",
        "packaging_specifications": "string"
      }
    },
    "economic_analysis": {
      "production_costs": {
        "seed_cost_per_hectare": "decimal",
        "fertilizer_cost": "decimal",
        "labor_cost": "decimal",
        "machinery_cost": "decimal",
        "total_cost_per_hectare": "decimal"
      },
      "market_prices": {
        "farm_gate_price": "decimal",
        "wholesale_price": "decimal",
        "retail_price": "decimal",
        "premium_price_available": "boolean",
        "price_volatility": "decimal"
      },
      "profitability_metrics": {
        "gross_margin_per_hectare": "decimal",
        "net_return_per_hectare": "decimal",
        "return_on_investment": "decimal",
        "break_even_yield": "decimal"
      }
    }
  }
}
```

## 2. 标准化分析输出格式

### 2.1 基因组选择分析结果格式

```json
{
  "genomic_selection_analysis": {
    "analysis_metadata": {
      "analysis_date": "YYYY-MM-DDTHH:MM:SSZ",
      "training_population_size": "integer",
      "validation_population_size": "integer",
      "marker_count": "integer",
      "method": ["GBLUP", "BayesB", "RRBLUP", "random_forest"],
      "software": "string"
    },
    "prediction_accuracy": {
      "trait_name": "string",
      "prediction_accuracy": "decimal >= 0.0, <= 1.0",
      "standard_error": "decimal",
      "cross_validation_results": {
        "mean_squared_error": "decimal",
        "correlation_coefficient": "decimal",
        "bias_estimate": "decimal"
      }
    },
    "selection_recommendations": [
      {
        "candidate_id": "string",
        "predicted_breeding_value": "decimal",
        "prediction_uncertainty": "decimal",
        "selection_rank": "integer",
        "probability_of_superiority": "decimal",
        "recommended_action": "select|test|reject|conditional"
      }
    ],
    "genetic_gain_projection": {
      "current_genetic_mean": "decimal",
      "projected_genetic_mean": "decimal",
      "expected_genetic_gain": "decimal",
      "time_to_achieve": "integer_years",
      "confidence_interval": {
        "lower": "decimal",
        "upper": "decimal"
      }
    }
  }
}
```

### 2.2 育种策略分析结果格式

```json
{
  "breeding_strategy_analysis": {
    "strategy_recommendations": {
      "primary_strategy": {
        "strategy_type": ["conventional", "molecular", "genomic", "speed_breeding", "gene_editing"],
        "rationale": "string",
        "expected_timeline": "integer_years",
        "resource_requirements": {
          "financial_investment": "decimal",
          "personnel_requirements": "integer",
          "infrastructure_needs": ["string"]
        },
        "success_probability": "decimal >= 0.0, <= 1.0"
      },
      "supporting_strategies": [
        {
          "strategy_name": "string",
          "integration_approach": "sequential|parallel|conditional",
          "timing": "string",
          "expected_contribution": "decimal"
        }
      ]
    },
    "crossing_recommendations": [
      {
        "cross_id": "string",
        "female_parent": "string",
        "male_parent": "string",
        "expected_heterosis": "decimal",
        "risk_assessment": {
          "compatibility_risk": "low|medium|high",
          "fertility_issues": "boolean",
          "segregation_distortion": "boolean"
        },
        "priority_rank": "integer",
        "estimated_success_rate": "decimal"
      }
    ],
    "selection_protocol": {
      "early_generation_selection": {
        "generation": "string",
        "selection_intensity": "decimal",
        "selection_criteria": ["string"],
        "expected_response": "decimal"
      },
      "advanced_generation_testing": {
        "test_locations": ["string"],
        "replication_design": "string",
        "statistical_power": "decimal >= 0.8",
        "environmental_representation": "string"
      }
    }
  }
}
```

### 2.3 专家咨询响应格式

```json
{
  "breeding_expert_consultation": {
    "response_metadata": {
      "consultation_id": "string",
      "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
      "expert_type": "crop_breeding_expert",
      "consultation_type": ["variety_development", "breeding_strategy", "germplasm_evaluation", "market_analysis"],
      "complexity_level": "basic|intermediate|advanced|expert"
    },
    "expert_analysis": {
      "problem_assessment": {
        "primary_breeding_objectives": ["string"],
        "constraints": ["string"],
        "opportunities": ["string"],
        "risk_factors": ["string"]
      },
      "technical_recommendations": [
        {
          "recommendation": "string",
          "scientific_basis": "string",
          "implementation_protocol": ["string"],
          "resource_requirements": "object",
          "expected_outcomes": "string",
          "timeline": "string"
        }
      ],
      "market_considerations": {
        "target_markets": ["string"],
        "competitive_advantages": ["string"],
        "market_entry_strategy": "string",
        "economic_projections": "object"
      }
    },
    "action_plan": {
      "immediate_actions": [
        {
          "action": "string",
          "priority": "high|medium|low",
          "timeframe": "string",
          "responsibility": "string"
        }
      ],
      "medium_term_goals": [
        {
          "goal": "string",
          "success_metrics": ["string"],
          "target_date": "YYYY-MM-DD"
        }
      ],
      "long_term_vision": {
        "strategic_objectives": ["string"],
        "milestone_markers": ["string"],
        "success_criteria": "string"
      }
    }
  }
}
```

## 3. 数据质量标准

### 3.1 育种数据质量评估标准

```json
{
  "breeding_data_quality_assessment": {
    "overall_quality_score": "decimal >= 0.0, <= 1.0",
    "data_completeness": {
      "phenotypic_data_completeness": "decimal >= 0.0, <= 1.0",
      "genotypic_data_completeness": "decimal >= 0.0, <= 1.0",
      "environmental_data_completeness": "decimal >= 0.0, <= 1.0",
      "missing_data_pattern": "random|systematic|clustered"
    },
    "data_consistency": {
      "experimental_design_compliance": "boolean",
      "data_entry_errors": "integer",
      "outlier_detection": {
        "statistical_outliers": "integer",
        "biological_outliers": "integer",
        "measurement_errors": "integer"
      }
    },
    "experimental_design_quality": {
      "statistical_power": "decimal >= 0.8",
      "randomization_effectiveness": "decimal",
      "block_effectiveness": "decimal",
      "replication_adequacy": "boolean"
    },
    "genotypic_data_quality": {
      "marker_call_rate": "decimal >= 0.95",
      "minor_allele_frequency_distribution": "object",
      "hardy_weinberg_equilibrium": "boolean",
      "linkage_disequilibrium_patterns": "object"
    }
  }
}
```

## 4. 使用指南

### 4.1 数据准备指南
1. 确保试验设计符合统计学原理
2. 提供完整的环境记录和管理实践信息
3. 验证基因型和表型数据的一致性
4. 确保市场数据的时效性和代表性

### 4.2 结果解读指南
1. 关注预测准确性的置信区间
2. 考虑G×E互作对育种值的稳定性影响
3. 评估经济可行性和市场风险
4. 制定基于科学证据的决策方案