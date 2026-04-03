package com.iflytek.rpa.auth.conf;

import com.alibaba.druid.pool.DruidDataSource;
import com.baomidou.mybatisplus.core.MybatisConfiguration;
import com.baomidou.mybatisplus.extension.spring.MybatisSqlSessionFactoryBean;
import com.iflytek.rpa.auth.sp.casdoor.dao.MarketUserDao;
import javax.sql.DataSource;
import org.apache.ibatis.session.SqlSessionFactory;
import org.mybatis.spring.SqlSessionTemplate;
import org.mybatis.spring.annotation.MapperScan;
import org.mybatis.spring.mapper.MapperFactoryBean;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;
import org.springframework.jdbc.datasource.DataSourceTransactionManager;

/**
 * 多数据源配置类
 * 仅在 casdoor 部署模式下生效
 *
 * @author Auto Generated
 */
@Configuration
@ConditionalOnProperty(name = "rpa.auth.deployment-mode", havingValue = "casdoor", matchIfMissing = false)
public class MultiDataSourceConfig {

    // ========== RPA 数据源配置 ==========
    @Value("${spring.datasource.url}")
    private String rpaUrl;

    @Value("${spring.datasource.username}")
    private String rpaUsername;

    @Value("${spring.datasource.password}")
    private String rpaPassword;

    @Value("${spring.datasource.driverClassName:com.mysql.cj.jdbc.Driver}")
    private String rpaDriverClassName;

    // ========== Casdoor 数据源配置 ==========
    @Value("${spring.datasource.casdoor.url}")
    private String casdoorUrl;

    @Value("${spring.datasource.casdoor.username}")
    private String casdoorUsername;

    @Value("${spring.datasource.casdoor.password}")
    private String casdoorPassword;

    @Value("${spring.datasource.casdoor.driverClassName:com.mysql.cj.jdbc.Driver}")
    private String casdoorDriverClassName;

    /**
     * RPA 数据源（主数据源）
     */
    @Bean(name = "rpaDataSource")
    @Primary
    public DataSource rpaDataSource() {
        DruidDataSource dataSource = new DruidDataSource();
        dataSource.setUrl(rpaUrl);
        dataSource.setUsername(rpaUsername);
        dataSource.setPassword(rpaPassword);
        dataSource.setDriverClassName(rpaDriverClassName);
        // Druid 连接池配置
        dataSource.setInitialSize(1);
        dataSource.setMinIdle(3);
        dataSource.setMaxActive(20);
        dataSource.setMaxWait(60000);
        dataSource.setTimeBetweenEvictionRunsMillis(60000);
        dataSource.setMinEvictableIdleTimeMillis(30000);
        dataSource.setValidationQuery("select 'x'");
        dataSource.setTestWhileIdle(true);
        dataSource.setTestOnBorrow(false);
        dataSource.setTestOnReturn(false);
        dataSource.setPoolPreparedStatements(true);
        dataSource.setMaxPoolPreparedStatementPerConnectionSize(20);
        try {
            dataSource.setFilters("stat,wall,slf4j");
        } catch (Exception e) {
            // ignore
        }
        dataSource.setConnectionProperties(
                "druid.stat.mergeSql=true;druid.stat.slowSqlMillis=2000;druid.stat.logSlowSql=true;druid.stat.enabled=true");
        return dataSource;
    }

    /**
     * Casdoor 数据源
     */
    @Bean(name = "casdoorDataSource")
    public DataSource casdoorDataSource() {
        DruidDataSource dataSource = new DruidDataSource();
        dataSource.setUrl(casdoorUrl);
        dataSource.setUsername(casdoorUsername);
        dataSource.setPassword(casdoorPassword);
        dataSource.setDriverClassName(casdoorDriverClassName);
        // Druid 连接池配置
        dataSource.setInitialSize(1);
        dataSource.setMinIdle(3);
        dataSource.setMaxActive(20);
        dataSource.setMaxWait(60000);
        dataSource.setTimeBetweenEvictionRunsMillis(60000);
        dataSource.setMinEvictableIdleTimeMillis(30000);
        dataSource.setValidationQuery("select 'x'");
        dataSource.setTestWhileIdle(true);
        dataSource.setTestOnBorrow(false);
        dataSource.setTestOnReturn(false);
        dataSource.setPoolPreparedStatements(true);
        dataSource.setMaxPoolPreparedStatementPerConnectionSize(20);
        try {
            dataSource.setFilters("stat,wall,slf4j");
        } catch (Exception e) {
            // ignore
        }
        dataSource.setConnectionProperties(
                "druid.stat.mergeSql=true;druid.stat.slowSqlMillis=2000;druid.stat.logSlowSql=true;druid.stat.enabled=true");
        return dataSource;
    }

    /**
     * RPA SqlSessionFactory
     */
    @Bean(name = "rpaSqlSessionFactory")
    @Primary
    public SqlSessionFactory rpaSqlSessionFactory(@Qualifier("rpaDataSource") DataSource dataSource) throws Exception {
        MybatisSqlSessionFactoryBean sessionFactory = new MybatisSqlSessionFactoryBean();
        sessionFactory.setDataSource(dataSource);
        // Mapper XML文件在Java源码目录下，编译后在classpath的对应包路径下
        sessionFactory.setMapperLocations(
                new PathMatchingResourcePatternResolver().getResources("classpath*:/com/iflytek/rpa/auth/**/*Dao.xml"));
        MybatisConfiguration configuration = new MybatisConfiguration();
        configuration.setMapUnderscoreToCamelCase(true);
        configuration.setLogImpl(org.apache.ibatis.logging.stdout.StdOutImpl.class);
        sessionFactory.setConfiguration(configuration);
        return sessionFactory.getObject();
    }

    /**
     * Casdoor SqlSessionFactory
     */
    @Bean(name = "casdoorSqlSessionFactory")
    public SqlSessionFactory casdoorSqlSessionFactory(@Qualifier("casdoorDataSource") DataSource dataSource)
            throws Exception {
        MybatisSqlSessionFactoryBean sessionFactory = new MybatisSqlSessionFactoryBean();
        sessionFactory.setDataSource(dataSource);
        // Mapper XML文件在Java源码目录下，编译后在classpath的对应包路径下
        sessionFactory.setMapperLocations(
                new PathMatchingResourcePatternResolver().getResources("classpath*:/com/iflytek/rpa/auth/**/*Dao.xml"));
        MybatisConfiguration configuration = new MybatisConfiguration();
        configuration.setMapUnderscoreToCamelCase(true);
        configuration.setLogImpl(org.apache.ibatis.logging.stdout.StdOutImpl.class);
        sessionFactory.setConfiguration(configuration);
        return sessionFactory.getObject();
    }

    /**
     * RPA SqlSessionTemplate
     */
    @Bean(name = "rpaSqlSessionTemplate")
    @Primary
    public SqlSessionTemplate rpaSqlSessionTemplate(@Qualifier("rpaSqlSessionFactory") SqlSessionFactory sqlSessionFactory) {
        return new SqlSessionTemplate(sqlSessionFactory);
    }

    /**
     * Casdoor SqlSessionTemplate
     */
    @Bean(name = "casdoorSqlSessionTemplate")
    public SqlSessionTemplate casdoorSqlSessionTemplate(
            @Qualifier("casdoorSqlSessionFactory") SqlSessionFactory sqlSessionFactory) {
        return new SqlSessionTemplate(sqlSessionFactory);
    }

    /**
     * RPA 事务管理器
     */
    @Bean(name = "rpaTransactionManager")
    @Primary
    public DataSourceTransactionManager rpaTransactionManager(@Qualifier("rpaDataSource") DataSource dataSource) {
        return new DataSourceTransactionManager(dataSource);
    }

    /**
     * Casdoor 事务管理器
     */
    @Bean(name = "casdoorTransactionManager")
    public DataSourceTransactionManager casdoorTransactionManager(@Qualifier("casdoorDataSource") DataSource dataSource) {
        return new DataSourceTransactionManager(dataSource);
    }

    /**
     * Casdoor相关DAO的MapperScan配置
     * 指定使用 casdoor 数据源（访问astron-agent-casdoor-mysql）
     * 扫描 com.iflytek.rpa.auth.sp.casdoor.dao 包，但 MarketUserDao 会被单独配置到 RPA 数据源
     */
    @Configuration
    @MapperScan(
            basePackages = "com.iflytek.rpa.auth.sp.casdoor.dao",
            sqlSessionFactoryRef = "casdoorSqlSessionFactory",
            sqlSessionTemplateRef = "casdoorSqlSessionTemplate")
    static class CasdoorDaoMapperScanConfig {
        // 空配置类，仅用于 @MapperScan 注解
    }

    /**
     * MarketUserDao的单独配置
     * 指定使用 rpa 数据源（访问rpa-opensource-mysql）
     * 注意：MarketUserDao 在 com.iflytek.rpa.auth.sp.casdoor.dao 包下，但需要使用 RPA 数据源
     * 因此需要手动注册，避免与 CasdoorDaoMapperScanConfig 冲突
     */
    @Bean
    public MapperFactoryBean<MarketUserDao> marketUserDao(
            @Qualifier("rpaSqlSessionFactory") SqlSessionFactory sqlSessionFactory) {
        MapperFactoryBean<MarketUserDao> factoryBean = new MapperFactoryBean<>(MarketUserDao.class);
        factoryBean.setSqlSessionFactory(sqlSessionFactory);
        return factoryBean;
    }

    /**
     * RPA业务数据库DAO的MapperScan配置
     * 指定使用 rpa 数据源（访问rpa-opensource-mysql）
     */
    @Configuration
    @MapperScan(
            basePackages = {
                    "com.iflytek.rpa.auth.auditRecord.dao",
                    "com.iflytek.rpa.auth.blacklist.dao",
                    "com.iflytek.rpa.auth.dataPreheater.dao"
            },
            sqlSessionFactoryRef = "rpaSqlSessionFactory",
            sqlSessionTemplateRef = "rpaSqlSessionTemplate")
    static class RpaBusinessDaoMapperScanConfig {
        // 空配置类，仅用于 @MapperScan 注解
    }

    /**
     * 数据源分配说明：
     * 1. CasdoorUserDao, CasdoorTenantDao, CasdoorRoleDao, CasdoorGroupDao 使用 casdoor 数据源（访问astron-agent-casdoor-mysql）
     * 2. 以下DAO使用 rpa 数据源（访问rpa-opensource-mysql）：
     *    - MarketUserDao（访问app_market_user表）
     *    - AuditRecordDao（访问audit_record表）
     *    - UserBlacklistDao（访问user_blacklist表）
     *    - SharedVarKeyTenantDao（访问shared_var_key_tenant表）
     *    - AppMarketUserDao（访问app_market_user表）
     *    - AppMarketDao（访问app_market表）
     *    - AppMarketClassificationDao（访问app_market_classification表）
     * 3. 对于跨数据源的查询（如getMarketUserList需要同时查询两个数据源），请在Service层分别查询后合并结果
     */
}

