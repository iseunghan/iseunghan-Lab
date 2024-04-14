package me.iseunghan.jpalab.repository;

import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import me.iseunghan.jpalab.entity.Member;
import me.iseunghan.jpalab.entity.Sponsor;
import me.iseunghan.jpalab.entity.Team;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.jdbc.AutoConfigureTestDatabase;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.test.context.TestPropertySource;

import java.util.List;

@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@TestPropertySource(properties = {
        "spring.jpa.properties.hibernate.default_batch_fetch_size=10",
})
public class JPA_FetchJoin_NotAllowed_On_Clause_Test {
    @Autowired
    private MemberRepository memberRepository;
    @Autowired
    private TeamRepository teamRepository;
    @PersistenceContext
    private EntityManager em;

    @BeforeEach
    void setup() {
        System.out.println("----------setup start-----------");
        Team team = Team.builder().name("team1").build();
        team.addMember(Member.builder().name("member11").build());
        team.addMember(Member.builder().name("member12").build());
        team.addSponsor(Sponsor.builder().name("sponsor11").build());
        teamRepository.save(team);

        Team team2 = Team.builder().name("team2").build();
        team2.addMember(Member.builder().name("member21").build());
        team2.addMember(Member.builder().name("member22").build());
        team2.addSponsor(Sponsor.builder().name("sponsor21").build());
        teamRepository.save(team2);

        Team team3 = Team.builder().name("team3").build();
        team3.addMember(Member.builder().name("member31").build());
        team3.addMember(Member.builder().name("member32").build());
        team3.addSponsor(Sponsor.builder().name("sponsor31").build());
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

    @DisplayName("join fetch는 on절 사용시 org.hibernate.query.SemanticException: Fetch join has a 'with' clause (use a filter instead) 발생")
    @Test
    void fetchJoin_NotAllow_On_condition() throws Exception {
        System.out.println("--------fetchJoin_NotAllow_On_condition START-------------");
        // when
        List<Team> teams = em.createQuery("select t from Team t join fetch t.members m on m.name = 'member11'", Team.class).getResultList();

        // then
        System.out.println("--------fetchJoin_NotAllow_On_condition MID-------------");
        teams.forEach(team -> {
            team.getMembers().stream().map(Member::getName).forEach(System.out::println);
            team.getSponsors().stream().map(Sponsor::getName).forEach(System.out::println);
        });
        System.out.println("--------fetchJoin_NotAllow_On_condition END-------------");
    }
}
