The writer takes a single table on the input.

- The table needs to contain column names exactly as they appear in destination Table.
- The table has to contain all Key attributes and all Attributes required by the destination table schema
- Other attributes may be included as required.
- The column should contain either a `scalar` value single string, number, etc. 
- Or an `object` value -> a valid JSON String or a JSON array string.
    - `scalar` type - the column contains a single value [e.g. string, number, ...]
    - `object` type - the column contains a valid JSON string. This allows exporting of a nested structures -> 
the nested structures must be serialized within the column values. e.g. 

    ```json
    {
    "name": "Test",
    "value": "1"
    }
    ```
    
    or a valid JSON array e.g. 
    
    ```json
    ["val1", "val2"]
    ```

  