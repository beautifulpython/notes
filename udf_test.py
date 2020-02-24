import numpy as np
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, pandas_udf, struct, PandasUDFType, udf, DataType


if __name__ == "__main__":
    spark = SparkSession \
        .builder \
        .appName("pandas_udf test") \
        .getOrCreate()
    
    spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")

    @pandas_udf("double", PandasUDFType.SCALAR)
    def add_udf(a, b):
        return a + b

    @pandas_udf('double', PandasUDFType.SCALAR)
    def pandas_plus_one(v):
        return v + 1
 
    df_pd = pd.DataFrame(data={'x': [1.1, 2.1, 3.1], 'y': [1.1, 2.1, 3.1]})
    points_df = spark.createDataFrame(df_pd)
    points_df.printSchema()
    points_df.createOrReplaceTempView("points")
    spark.sql("select x,y from points").show()
    spark.udf.register("add_udf",add_udf)
    spark.sql("select add_udf(x,y) from points").show()
    
    spark.stop()
