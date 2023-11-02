package {group_id}.controller;

import {group_id}.dao.model.{model_name_upper_camel};
import {group_id}.service.{model_name_upper_camel}Service;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
public class {model_name_upper_camel}Controller {
    @Autowired
    private {model_name_upper_camel}Service {model_name_lower_camel}Service;

    @GetMapping("all")
    public List<{model_name_upper_camel}> getAll() {
        return {model_name_lower_camel}Service.getAll{model_name_upper_camel}s();
    }

    @GetMapping("{model_name_lower_camel}/{id}")
    public {model_name_upper_camel} getById(@PathVariable("id") String id) {
        return {model_name_lower_camel}Service.get{model_name_upper_camel}ById(id);
    }
}
