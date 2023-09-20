package me.iseunghan.springtest.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import lombok.*;

@Getter
@AllArgsConstructor(staticName = "of")
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class CreateAccountDto {
    @NotBlank(message = "이름은 비어 있을 수 없습니다.")
    private String name;
    @Min(value = 1, message = "나이는 1살 이상이여야 합니다.")
    private int age;
}
