# SpringBoot를 이용한 ZIP 파일 핸들링을 예제 코드를 통해 배워봅시다.
## API
### ZIP Upload
```http request
###
POST http://localhost:8080/api/v1/zip-upload?
    dstPath={{$random.alphanumeric(8)}}
    Content-Type: multipart/form-data
```

### Downloads folder converted to ZIP
```http request
###
GET http://localhost:8080/api/v1/file-zipping-and-download?
    folderName={{$random.alphanumeric(8)}}
```

### multipart configuration
```json
spring:
  servlet:
    multipart:
      file-size-threshold: 1MB
      max-file-size: 500MB
      max-request-size: 1GB
```
[링크 참조](https://spring.io/guides/gs/uploading-files)

## Test with PostMan
* JSON 파일을 Postman을 이용해 업로드하여 사용 - [spring-zip-unzip.postman_collection.json](spring-zip-unzip.postman_collection.json)