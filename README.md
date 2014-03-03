# CommonsCloudAPI


## API Documentation

All API endpoints are based on the assumed base url of https://api.commonscloud.org/v2/<endpoint::details>

#### /application

| Method | URL | Description | Return | Sample Response
| --- | --- | --- | ---
| GET | /application/ | Show a list of my applications | (array) | (response)[]


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



| Method | URL | Description | Sample Response |
| --- | --- | --- | --- |
| GET | /application/ | Show a list of my applications | `grr`
| GET | /application/<application_id>/ | Show a single application | ggg


##### /template

##### /field

##### /statistic

##### /feature

##### errors


### Version

We are currently in a "development" state, anything may change at any time. The public API should not be considered stable. We are attempting to conform to Semantic Versioning 2.0.0 for our releases. If you see anything that does not align with this protocol of versioning, [please submit an Issue via Github](https://github.com/CommonsCloud/CommonsCloudAPI/issues) or you may submit a pull request as well.

For more information on what our version numbers mean, please see http://semver.org/