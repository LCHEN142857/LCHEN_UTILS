package {group_id}.service;

import {group_id}.dao.model.{model_name_upper_camel};

import java.util.List;

public interface {model_name_upper_camel}Service {
    List<{model_name_upper_camel}> getAll{model_name_upper_camel}s();

    {model_name_upper_camel} get{model_name_upper_camel}ById(String id);
}
