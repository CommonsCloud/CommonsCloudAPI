# CommonsCloudAPI


## API Documentation

All API endpoints are based on the assumed base url of https://api.commonscloud.org/v2/[endpoint]

#### /application

| Method | URL | Description | Example
| --- | --- | --- | --- | --- | ---
| GET | /application/ | Show a list of my applications | [example](#get-application)
| POST | /application/ | Create a new application |
| GET | /application/&lt;Application ID&gt; | Show an existing application | [example](#get-application1)


###### [GET] /application
```javascript
{
  "response": {
    "applications": [
      {
        "created": "Mon, 03 Mar 2014 14:41:15 GMT",
        "description": "",
        "id": 1,
        "name": "My Project Name",
        "status": true,
        "url": "http://www.mycommonscloud.com/"
      }
    ]
  }
}
```

###### [GET] /application/1
```javascript
{
  "response": {
    "created": "Mon, 03 Mar 2014 14:41:15 GMT",
    "description": "",
    "id": 1,
    "name": "My Project Name",
    "status": true,
    "url": "http://www.mycommonscloud.com/"
  }
}
```


#### /template

#### /field

#### /statistic

#### /feature

#### errors

From time to time you'll run into an error message within the system, below we've outlined what you may encounter. In the future we'll add possible solutions for each of these.

| Code | Status | Solution
| --- | --- | ---
| 415 | Unsupported Media Type | This normally happens when you forget to append a 'Content-Type' header to the request or when you ask for a format that we don't support. CommonsCloud currently supports text/csv and application/json Content-Types and can also support the 'format' URL parameter with either json or csv as the value

### Version

We are currently in a "development" state, anything may change at any time. The public API should not be considered stable. We are attempting to conform to Semantic Versioning 2.0.0 for our releases. If you see anything that does not align with this protocol of versioning, [please submit an Issue via Github](https://github.com/CommonsCloud/CommonsCloudAPI/issues) or you may submit a pull request as well.

For more information on what our version numbers mean, please see http://semver.org/