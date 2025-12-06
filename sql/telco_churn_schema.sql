-- ===================================================================
-- TelcoGuard: Customer Churn Prediction Database Schema
-- ===================================================================
-- This schema implements a star design for analytics
-- Bronze (Raw) -> Silver (Cleaned) -> Gold (Analytics)
-- ===================================================================

-- ===================== DIMENSION TABLES =====================

-- Customer Dimension Table
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(15),
    signup_date DATE NOT NULL,
    contract_type VARCHAR(30) NOT NULL,
    contract_duration_months INT,
    is_senior_citizen BOOLEAN DEFAULT FALSE,
    has_dependents BOOLEAN DEFAULT FALSE,
    has_partner BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_signup_date (signup_date),
    INDEX idx_contract_type (contract_type)
);

-- Service Dimension Table
CREATE TABLE IF NOT EXISTS dim_service (
    service_id INT AUTO_INCREMENT PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    service_category VARCHAR(50) NOT NULL,
    base_price DECIMAL(10,2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_service (service_name, service_category),
    INDEX idx_category (service_category)
);

-- Time Dimension Table
CREATE TABLE IF NOT EXISTS dim_time (
    time_id INT AUTO_INCREMENT PRIMARY KEY,
    calendar_date DATE NOT NULL UNIQUE,
    year INT NOT NULL,
    month INT NOT NULL,
    quarter INT NOT NULL,
    day_of_week VARCHAR(10) NOT NULL,
    week_of_year INT NOT NULL,
    is_month_end BOOLEAN DEFAULT FALSE,
    is_quarter_end BOOLEAN DEFAULT FALSE,
    INDEX idx_calendar_date (calendar_date),
    INDEX idx_year_month (year, month)
);

-- ===================== FACT TABLES =====================

-- Monthly Usage Fact Table
CREATE TABLE IF NOT EXISTS fact_monthly_usage (
    usage_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    time_id INT NOT NULL,
    tenure_months INT NOT NULL,
    monthly_charges DECIMAL(10,2) NOT NULL,
    total_charges DECIMAL(12,2) NOT NULL,
    internet_service_type VARCHAR(30),
    phone_service BOOLEAN DEFAULT FALSE,
    streaming_tv BOOLEAN DEFAULT FALSE,
    streaming_movies BOOLEAN DEFAULT FALSE,
    online_backup BOOLEAN DEFAULT FALSE,
    device_protection BOOLEAN DEFAULT FALSE,
    tech_support BOOLEAN DEFAULT FALSE,
    churn_flag BOOLEAN DEFAULT FALSE,
    churn_date DATE,
    churned_days INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (time_id) REFERENCES dim_time(time_id),
    INDEX idx_customer_date (customer_id, time_id),
    INDEX idx_churn_flag (churn_flag),
    INDEX idx_monthly_charges (monthly_charges),
    INDEX idx_tenure (tenure_months)
);

-- Customer Service Usage Fact Table
CREATE TABLE IF NOT EXISTS fact_service_usage (
    service_usage_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    service_id INT NOT NULL,
    time_id INT NOT NULL,
    usage_quantity INT,
    service_charges DECIMAL(10,2),
    is_active BOOLEAN DEFAULT TRUE,
    activated_date DATE,
    deactivated_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (service_id) REFERENCES dim_service(service_id),
    FOREIGN KEY (time_id) REFERENCES dim_time(time_id),
    INDEX idx_customer_service (customer_id, service_id)
);

-- ===================== AGGREGATE TABLES (Pre-computed) =====================

CREATE TABLE IF NOT EXISTS agg_churn_by_segment (
    segment_id INT AUTO_INCREMENT PRIMARY KEY,
    segment_name VARCHAR(100),
    time_id INT NOT NULL,
    total_customers INT,
    churned_customers INT,
    churn_rate DECIMAL(5,4),
    avg_tenure DECIMAL(8,2),
    avg_monthly_charges DECIMAL(10,2),
    avg_total_charges DECIMAL(12,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (time_id) REFERENCES dim_time(time_id),
    INDEX idx_segment_time (segment_name, time_id)
);

-- ===================== VIEWS FOR ANALYTICS =====================

-- Customer Churn Analytics View with Window Functions
CREATE VIEW vw_customer_churn_analysis AS
SELECT 
    c.customer_id,
    CONCAT(c.first_name, ' ', c.last_name) as customer_name,
    c.signup_date,
    c.contract_type,
    fmu.tenure_months,
    fmu.monthly_charges,
    fmu.total_charges,
    fmu.churn_flag,
    fmu.churn_date,
    
    -- Window Functions
    ROW_NUMBER() OVER (ORDER BY fmu.total_charges DESC) as revenue_rank,
    RANK() OVER (PARTITION BY c.contract_type ORDER BY fmu.tenure_months DESC) as tenure_rank_by_contract,
    LAG(fmu.monthly_charges) OVER (PARTITION BY c.customer_id ORDER BY fmu.time_id) as prev_monthly_charges,
    LEAD(fmu.monthly_charges) OVER (PARTITION BY c.customer_id ORDER BY fmu.time_id) as next_monthly_charges,
    PERCENT_RANK() OVER (ORDER BY fmu.monthly_charges) as charge_percentile,
    
    -- Risk Indicators
    CASE 
        WHEN fmu.churn_flag = TRUE THEN 'Churned'
        WHEN fmu.tenure_months <= 12 AND fmu.monthly_charges > 100 THEN 'High Risk'
        WHEN fmu.tenure_months <= 24 THEN 'Medium Risk'
        ELSE 'Low Risk'
    END as risk_segment,
    
    -- Value Segment
    CASE 
        WHEN fmu.total_charges > 5000 THEN 'High Value'
        WHEN fmu.total_charges > 2000 THEN 'Medium Value'
        ELSE 'Low Value'
    END as customer_value
    
FROM dim_customer c
LEFT JOIN fact_monthly_usage fmu ON c.customer_id = fmu.customer_id;

-- Cohort Analysis View
CREATE VIEW vw_cohort_analysis AS
SELECT 
    c.customer_id,
    YEAR(c.signup_date) as signup_year,
    MONTH(c.signup_date) as signup_month,
    YEARMONTH(c.signup_date) as signup_cohort,
    fmu.tenure_months,
    fmu.churn_flag,
    COUNT(*) OVER (PARTITION BY YEARMONTH(c.signup_date)) as cohort_size,
    SUM(CASE WHEN fmu.churn_flag = TRUE THEN 1 ELSE 0 END) 
        OVER (PARTITION BY YEARMONTH(c.signup_date)) as churned_count,
    ROUND(SUM(CASE WHEN fmu.churn_flag = TRUE THEN 1 ELSE 0 END) 
        OVER (PARTITION BY YEARMONTH(c.signup_date)) / 
        COUNT(*) OVER (PARTITION BY YEARMONTH(c.signup_date)) * 100, 2) as cohort_churn_rate
FROM dim_customer c
LEFT JOIN fact_monthly_usage fmu ON c.customer_id = fmu.customer_id;

-- Monthly Retention Metrics View
CREATE VIEW vw_monthly_retention AS
SELECT 
    t.calendar_date,
    t.year,
    t.month,
    COUNT(DISTINCT CASE WHEN fmu.churn_flag = FALSE THEN fmu.customer_id END) as retained_customers,
    COUNT(DISTINCT CASE WHEN fmu.churn_flag = TRUE THEN fmu.customer_id END) as churned_customers,
    COUNT(DISTINCT fmu.customer_id) as total_active,
    ROUND(COUNT(DISTINCT CASE WHEN fmu.churn_flag = FALSE THEN fmu.customer_id END) / 
        COUNT(DISTINCT fmu.customer_id) * 100, 2) as retention_rate,
    AVG(fmu.monthly_charges) as avg_monthly_charge,
    AVG(fmu.tenure_months) as avg_tenure
FROM dim_time t
LEFT JOIN fact_monthly_usage fmu ON t.time_id = fmu.time_id
GROUP BY t.time_id, t.calendar_date, t.year, t.month;

-- ===================== STORED PROCEDURES =====================

-- Procedure: Calculate Churn Rate by Segment
DELIMITER //
CREATE PROCEDURE sp_calculate_churn_by_segment()
BEGIN
    INSERT INTO agg_churn_by_segment (segment_name, time_id, total_customers, churned_customers, churn_rate)
    SELECT 
        c.contract_type as segment_name,
        fmu.time_id,
        COUNT(DISTINCT c.customer_id) as total_customers,
        COUNT(DISTINCT CASE WHEN fmu.churn_flag = TRUE THEN c.customer_id END) as churned_customers,
        ROUND(COUNT(DISTINCT CASE WHEN fmu.churn_flag = TRUE THEN c.customer_id END) / 
            COUNT(DISTINCT c.customer_id), 4) as churn_rate
    FROM dim_customer c
    LEFT JOIN fact_monthly_usage fmu ON c.customer_id = fmu.customer_id
    GROUP BY c.contract_type, fmu.time_id
    ON DUPLICATE KEY UPDATE 
        total_customers = VALUES(total_customers),
        churned_customers = VALUES(churned_customers),
        churn_rate = VALUES(churn_rate);
END //
DELIMITER ;

-- Procedure: Get High-Risk Customers
DELIMITER //
CREATE PROCEDURE sp_get_high_risk_customers(IN risk_threshold DECIMAL(4,2))
BEGIN
    SELECT 
        c.customer_id,
        CONCAT(c.first_name, ' ', c.last_name) as customer_name,
        c.email,
        fmu.tenure_months,
        fmu.monthly_charges,
        fmu.total_charges,
        CASE 
            WHEN fmu.tenure_months <= 12 AND fmu.monthly_charges > 100 THEN 'High'
            WHEN fmu.tenure_months <= 24 THEN 'Medium'
            ELSE 'Low'
        END as churn_risk,
        fmu.internet_service_type,
        fmu.tech_support,
        fmu.phone_service
    FROM dim_customer c
    LEFT JOIN fact_monthly_usage fmu ON c.customer_id = fmu.customer_id
    WHERE fmu.tenure_months <= 12 
    AND fmu.monthly_charges > risk_threshold
    ORDER BY fmu.monthly_charges DESC;
END //
DELIMITER ;

-- ===================== INDEXES FOR PERFORMANCE =====================

CREATE INDEX idx_fact_usage_customer ON fact_monthly_usage(customer_id);
CREATE INDEX idx_fact_usage_churn ON fact_monthly_usage(churn_flag);
CREATE INDEX idx_fact_usage_charges ON fact_monthly_usage(monthly_charges);
CREATE INDEX idx_fact_service_customer ON fact_service_usage(customer_id);
CREATE INDEX idx_dim_customer_signup ON dim_customer(signup_date);

-- ===================== SAMPLE DATA LOADING =====================

-- Insert sample time dimension data (2024)
INSERT INTO dim_time (calendar_date, year, month, quarter, day_of_week, week_of_year, is_month_end, is_quarter_end)
VALUES
('2024-01-01', 2024, 1, 1, 'Monday', 1, FALSE, FALSE),
('2024-01-31', 2024, 1, 1, 'Wednesday', 5, TRUE, FALSE),
('2024-02-29', 2024, 2, 1, 'Thursday', 9, TRUE, FALSE),
('2024-03-31', 2024, 3, 1, 'Sunday', 13, TRUE, TRUE);

-- ===================== QUERY EXAMPLES FOR ANALYSIS =====================

-- Query 1: Churn Rate by Contract Type (with percentages)
-- SELECT contract_type, 
--        COUNT(*) as total_customers,
--        SUM(CASE WHEN churn_flag = TRUE THEN 1 ELSE 0 END) as churned,
--        ROUND(SUM(CASE WHEN churn_flag = TRUE THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) as churn_rate
-- FROM vw_customer_churn_analysis
-- GROUP BY contract_type
-- ORDER BY churn_rate DESC;

-- Query 2: Cohort Analysis - Retention by Sign-up Month
-- SELECT signup_cohort, 
--        FLOOR(tenure_months / 12) as year,
--        COUNT(*) as customers,
--        ROUND(SUM(CASE WHEN churn_flag = TRUE THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) as churn_rate
-- FROM vw_cohort_analysis
-- GROUP BY signup_cohort, year
-- ORDER BY signup_cohort, year;

-- Query 3: Monthly Trend Analysis
-- SELECT calendar_date, 
--        retained_customers,
--        churned_customers,
--        retention_rate,
--        avg_monthly_charge
-- FROM vw_monthly_retention
-- WHERE calendar_date >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
-- ORDER BY calendar_date DESC;

-- Query 4: Customer Segmentation with CTEs
-- WITH customer_segments AS (
--     SELECT customer_id,
--            tenure_months,
--            monthly_charges,
--            CASE 
--                WHEN tenure_months >= 24 AND monthly_charges > 80 THEN 'VIP'
--                WHEN tenure_months >= 12 AND monthly_charges > 60 THEN 'Regular'
--                ELSE 'New'
--            END as segment
--     FROM fact_monthly_usage
-- )
-- SELECT segment,
--        COUNT(*) as customer_count,
--        AVG(monthly_charges) as avg_spend,
--        MAX(tenure_months) as max_tenure
-- FROM customer_segments
-- GROUP BY segment;

-- =====================================================================
-- End of Schema Definition
-- =====================================================================
