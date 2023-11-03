package {group_id}.service.impl;

import {group_id}.dao.mapper.{model_name_upper_camel}Mapper;
import {group_id}.dao.model.{model_name_upper_camel};
import {group_id}.service.{model_name_upper_camel}Service;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class {model_name_upper_camel}ServiceImpl implements {model_name_upper_camel}Service {
    @Autowired
    private {model_name_upper_camel}Mapper {model_name_lower_camel}Mapper;

    @Override
    public List<{model_name_upper_camel}> getAll{model_name_upper_camel}s() {
        return {model_name_lower_camel}Mapper.getAll();
    }

    @Override
    public {model_name_upper_camel} get{model_name_upper_camel}ById(String id) {
        return {model_name_lower_camel}Mapper.selectById(id);
    }


}
