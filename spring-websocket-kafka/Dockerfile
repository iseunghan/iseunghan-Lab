# 1단계: 빌드 스테이지
FROM gradle:8.11.0-jdk17 AS build

# 작업 디렉토리 설정
WORKDIR /app

# Gradle 캐시 최적화
COPY build.gradle settings.gradle gradlew /app/
COPY gradle ./gradle
# Gradle 의존성 캐시 다운로드 (빌드 속도 최적화)
RUN ./gradlew dependencies --no-daemon || true

# 소스 복사
COPY src ./src

# 빌드 실행 (테스트 포함)
RUN ./gradlew clean build --no-daemon

# 2단계: 실행 스테이지 (경량 JRE, ARM64 지원)
FROM eclipse-temurin:17-jre

WORKDIR /app
# builder에서 빌드된 JAR 복사
COPY --from=build /app/build/libs/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]