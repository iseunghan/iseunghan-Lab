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
import org.springframework.data.domain.PageRequest;
import org.springframework.test.context.TestPropertySource;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@TestPropertySource(properties = {
        "spring.jpa.properties.hibernate.default_batch_fetch_size=10",
})
public class Team_MultipleBagEx_Solution2_Test {
    @Autowired private MemberRepository memberRepository;
    @Autowired private TeamRepository teamRepository;
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

    @DisplayName("둘 이상의 컬렉션을 페치조인할 수 없다 -> Fetch Join(x) + BatchSize를 이용해 해결")
    @Test
    void Over_Two_collection_Not_Used_fetchJoin_and_Use_BatchSize() throws Exception {
        System.out.println("--------Over_Two_collection_Not_Used_fetchJoin_and_Use_BatchSize START-------------");
        // when
        List<Team> teams = teamRepository.findAll(PageRequest.of(0, 3)).getContent();
        assertThat(teams).hasSize(3);

        // then
        System.out.println("--------Over_Two_collection_Not_Used_fetchJoin_and_Use_BatchSize MID-------------");
        teams.forEach(team -> {
            System.out.println(team.getName());
            team.getMembers().stream().map(Member::getName).forEach(System.out::println);
            team.getSponsors().stream().map(Sponsor::getName).forEach(System.out::println);
        });

        System.out.println("--------Over_Two_collection_Not_Used_fetchJoin_and_Use_BatchSize END-------------");
    }
}
