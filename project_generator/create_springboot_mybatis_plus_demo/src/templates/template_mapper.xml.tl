<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="{group_id}.dao.mapper.{model_name_upper_camel}Mapper">
    <resultMap id="BaseResultMap" type="{group_id}.dao.model.{model_name_upper_camel}">
        <result column="{column_1}" jdbcType="VARCHAR" property="{column_camel_1}"/>
    </resultMap>
    <sql id="Base_Column_List">
        {column_list}
    </sql>
    <select id="getAll" resultMap="BaseResultMap">
        SELECT
        <include refid="Base_Column_List"/>
        FROM {table_name};
    </select>

</mapper>
