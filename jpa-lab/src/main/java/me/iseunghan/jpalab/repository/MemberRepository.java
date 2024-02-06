package me.iseunghan.jpalab.repository;

import me.iseunghan.jpalab.entity.Member;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;

public interface MemberRepository extends JpaRepository<Member, Long> {
    @Query(value = "select m from Member m join fetch m.team")
    List<Member> findMembersFetchJoin();
    @EntityGraph(attributePaths = "team")
    @Query(value = "select m from Member m")
    List<Member> findMembersEntityGraph();
}
