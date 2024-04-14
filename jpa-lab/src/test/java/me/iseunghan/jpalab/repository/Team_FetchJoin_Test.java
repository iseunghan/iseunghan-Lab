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
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
public class Team_FetchJoin_Test {
    @Autowired
    private MemberRepository memberRepository;
    @Autowired private TeamRepository teamRepository;
    @PersistenceContext
    private EntityManager em;

    @BeforeEach
    void setup() {
        System.out.println("----------setup start-----------");
        Sponsor sponsor11 = Sponsor.builder().name("sponsor11").build();
        Sponsor sponsor12 = Sponsor.builder().name("sponsor12").build();
        Team team1 = Team.builder().name("team1").build();
        team1.addMember(Member.builder().name("member1-1").build());
        team1.addMember(Member.builder().name("member1-2").build());
        team1.addSponsor(sponsor11);
        team1.addSponsor(sponsor12);

        Sponsor sponsor21 = Sponsor.builder().name("sponsor21").build();
        Sponsor sponsor22 = Sponsor.builder().name("sponsor22").build();
        Team team2 = Team.builder().name("team2").build();
        team2.addMember(Member.builder().name("member2-1").build());
        team2.addMember(Member.builder().name("member2-2").build());
//        team2.addSponsor(sponsor21);
//        team2.addSponsor(sponsor22);

        Sponsor sponsor31 = Sponsor.builder().name("sponsor31").build();
        Sponsor sponsor32 = Sponsor.builder().name("sponsor32").build();
        Team team3 = Team.builder().name("team3").build();
        team3.addMember(Member.builder().name("member3-1").build());
        team3.addMember(Member.builder().name("member3-2").build());
        team3.addSponsor(sponsor31);
        team3.addSponsor(sponsor32);

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

    @DisplayName("둘 이상의 컬렉션을 페치조인할 수 없다.")
    @Test
    void Over_Two_collection_fetchJoin_Not_Allowed() throws Exception {
        System.out.println("--------Over_Two_collection_fetchJoin_Not_Allowed START-------------");
        // when
        List<Team> teams = teamRepository.findTeamsFetchJoinTwoCollection(PageRequest.of(0, 3)).getContent();
        assertThat(teams).hasSize(3);

        // then
        System.out.println("--------Over_Two_collection_fetchJoin_Not_Allowed MID-------------");
        teams.forEach(team -> {
            System.out.println(team.getName());
            team.getMembers().stream().map(Member::getName).forEach(System.out::println);
            team.getSponsors().stream().map(Sponsor::getName).forEach(System.out::println);
        });

        System.out.println("--------Over_Two_collection_fetchJoin_Not_Allowed END-------------");
    }
}
