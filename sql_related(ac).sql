USE ac;

CREATE TABLE info(url VARCHAR(255), stock_status VARCHAR(255), model_no VARCHAR(255), brand_name VARCHAR(255), ac_type VARCHAR(255), horsepower FLOAT, price INT
                  , broadway_code VARCHAR(255), area_low_lim INT, area_up_lim INT, PRIMARY KEY(url));

CREATE TABLE feature(url VARCHAR(255), feature VARCHAR(255));

CREATE TABLE brand(brand_name VARCHAR(255), PRIMARY KEY(brand_name));

CREATE INDEX idx_url ON info (url);

CREATE INDEX idx_url ON feature (url);