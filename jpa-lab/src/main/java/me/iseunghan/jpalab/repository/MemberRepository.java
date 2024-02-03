package me.iseunghan.jpalab.repository;

import me.iseunghan.jpalab.entity.Member;
import org.springframework.data.jpa.repository.JpaRepository;

public interface MemberRepository extends JpaRepository<Member, Long> {
}
