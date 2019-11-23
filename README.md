# KBC Component Python template

A simple KBC writer component that allows to export data from KBC to an **existing table** in DynamoDB.


## Configuration

The writer takes a single table on the input.

- The table needs to contain column names exactly as they appear in destination Table.
- The table has to contain all Key attributes and all Attributes required by the destination table schema
- Other attributes may be included as required.
- The column should contain either a `scalar` value single string, number, etc. 
- Or an `object` value -> a valid JSON String or a JSON array string.
- Column values may be `gzipped` and stored as Binary values.


### Parameters

- **AWS Access Key ID** - valid AWS Access Key ID
- **AWS Access Key Secret** - valid AWS Access Key Secret
- **Region** - AWS region
- **Destination Table name** - name of the existing destination table exactly as is.
- **Column Configuration** - Configuration of the input columns. The names must appear exactly as they are in the destination and 
the source table. The column type must be set to its appropriate value. 
    - `scalar` type - the column contains a single value [e.g. string, number, ...]
    - `object` type - the column contains a valid JSON string. This allows exporting of nested structures -> 
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
  - `gzip` type - any content in the column will be gzipped and stored as `Binary` value


### Example
 
The following table row:


| id       | timestamp | value                                                 |
|----------|-----------|-------------------------------------------------------|
| 123456 | 123456789  | [{"name":"val1","value":1},{"name":"val2","value":0}] |


Leads to this item in DynamoDB:

```json
{
  "timestamp": "123456789",
  "id": "123456",
  "value": [
    {
      "name": "val1",
      "value": 1
    },
    {
      "name": "val2",
      "value": 0
    }
  ]  
}
```

**Column configuration:**

- timestamp : `scalar`
- id: `scalar`
- value: `object` 
 
## Development
 
This example contains runnable container with simple unittest. For local testing it is useful to include `data` folder in the root
and use docker-compose commands to run the container or execute tests. 

If required, change local data folder (the `CUSTOM_FOLDER` placeholder) path to your custom path:
```yaml
    volumes:
      - ./:/code
      - ./CUSTOM_FOLDER:/data
```

Clone this repository, init the workspace and run the component with following command:

```
git clone https://bitbucket.org:kds_consulting_team/kds-team.ex-dynamodb.git
cd kds-team.ex-dynamodb
docker-compose build
docker-compose run --rm dev
```

Run the test suite and lint check using this command:

```
docker-compose run --rm test
```

# Integration

For information about deployment and integration with KBC, please refer to the [deployment section of developers documentation](https://developers.keboola.com/extend/component/deployment/) 