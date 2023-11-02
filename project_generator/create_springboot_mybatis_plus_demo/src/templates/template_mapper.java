package {group_id}.dao.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;
import {group_id}.dao.model.{model_name_upper_camel};

import java.util.List;

@Mapper
public interface {model_name_upper_camel}Mapper extends BaseMapper<{model_name_upper_camel}> {
    List<{model_name_upper_camel}> getAll{model_name_upper_camel}s();
}
