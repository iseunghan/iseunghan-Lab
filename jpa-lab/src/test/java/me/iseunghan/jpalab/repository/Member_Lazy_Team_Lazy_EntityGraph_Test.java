package me.iseunghan.jpalab.repository;

import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import me.iseunghan.jpalab.entity.Member;
import me.iseunghan.jpalab.entity.Team;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.jdbc.AutoConfigureTestDatabase;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.data.domain.PageRequest;

import java.util.List;
import java.util.Set;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
public class Member_Lazy_Team_Lazy_EntityGraph_Test {
    @Autowired private MemberRepository memberRepository;
    @Autowired private TeamRepository teamRepository;
    @PersistenceContext private EntityManager em;

    @BeforeEach
    void setup() {
        System.out.println("----------setup start-----------");
        Team team1 = Team.builder().name("team1").build();
        team1.addMember(Member.builder().name("member1-1").build());
        team1.addMember(Member.builder().name("member1-2").build());

        Team team2 = Team.builder().name("team2").build();
        team2.addMember(Member.builder().name("member2-1").build());
        team2.addMember(Member.builder().name("member2-2").build());

        Team team3 = Team.builder().name("team3").build();
        team3.addMember(Member.builder().name("member3-1").build());
        team3.addMember(Member.builder().name("member3-2").build());

        teamRepository.save(team1);
        teamRepository.save(team2);
        teamRepository.save(team3);

        clearPersistenceContext();
        System.out.println("----------setup end-----------");
    }

    @AfterEach
    void clear() {
        System.out.println("----------clear start-----------");
        memberRepository.deleteAll();
        teamRepository.deleteAll();
        clearPersistenceContext();
        System.out.println("----------clear end-----------");
    }

    private void clearPersistenceContext() {
        em.flush();
        em.clear();
    }

    @DisplayName("단일 팀을 조회하고, 멤버를 사용하던 안하던 -> 1개의 쿼리가 나간다.(팀 조회하는 쿼리 1개)")
    @Test
    void find_One_Team_test() {
        clearPersistenceContext();

        System.out.println("----------find_One_Team_test start-----------");
        Team team = teamRepository.findTeamByNameEntityGraph("team1")
                .orElseThrow(RuntimeException::new);
        assertThat(team.getName()).isEqualTo("team1");
        System.out.println("----------find_One_Team_test end-----------");
    }

    @DisplayName("모든 팀을 조회하고, 지연로딩 된 멤버를 사용할 때 -> 단 1개의 쿼리만 나간다")
    @Test
    void team_findAll_test() {
        clearPersistenceContext();

        System.out.println("----------team_findAll_test start-----------");
        List<Team> teamList = teamRepository.findTeamsEntityGraph();
        assertThat(teamList).hasSize(3);
        System.out.println("----------team_findAll_test mid-----------");
        teamList.stream()
                .map(Team::getMembers)
                .map(List::stream)
                .forEach(memberStream -> memberStream
                        .map(Member::getName)
                        .forEach(System.out::println)
                );
        System.out.println("----------team_findAll_test end-----------");
    }

    @DisplayName("모든 팀을 조회할 때, EntityGraph + Pageable은 Limit 쿼리가 안나간다.")
    @Test
    void team_findAll_Pagination_test() {
        clearPersistenceContext();

        System.out.println("----------team_findAll_test start-----------");
        List<Team> teamList = teamRepository.findTeamsEntityGraph(PageRequest.of(0, 1));
        assertThat(teamList).hasSize(1);
        System.out.println("----------team_findAll_test mid-----------");
        teamList.stream()
                .map(Team::getMembers)
                .map(List::stream)
                .forEach(memberStream -> memberStream
                        .map(Member::getName)
                        .forEach(System.out::println)
                );
        System.out.println("----------team_findAll_test end-----------");
    }

    @DisplayName("모든 멤버를 조회하고, 지연로딩 된 팀을 사용할 때 -> 단 1개의 쿼리만 나간다")
    @Test
    void member_findAll_test() {
        clearPersistenceContext();

        System.out.println("----------member_findAll_test start-----------");
        List<Member> memberList = memberRepository.findMembersEntityGraph();
        assertThat(memberList).hasSize(6);
        System.out.println("----------member_findAll_test mid-----------");
        memberList.stream()
                .map(Member::getTeam)
                .map(Team::getName)
                .forEach(System.out::println);
        System.out.println("----------member_findAll_test end-----------");
    }
}
