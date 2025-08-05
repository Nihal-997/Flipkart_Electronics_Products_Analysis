create table products(
id serial,
product_type text,
title text,
specifications text,
star_rating float,
rating_count float,
review_count float,
original_price float,
discounted_price float,
discount_percentage float,
image_url text
);

select * from products