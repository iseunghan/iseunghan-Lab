package me.iseunghan.jpalab.entity;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.BatchSize;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Entity
public class Team {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;

//    @BatchSize(size = 10)
    @OneToMany(mappedBy = "team", fetch = FetchType.LAZY, cascade = CascadeType.ALL)
    private Set<Member> members = new LinkedHashSet<>();

    @OneToMany(mappedBy = "team", fetch = FetchType.LAZY, cascade = CascadeType.ALL)
    private Set<Sponsor> sponsors = new LinkedHashSet<>();

    @Builder
    private Team(String name) {
        this.name = name;
    }

    public void addMember(Member member) {
        this.members.add(member);
        member.updateTeam(this);
    }

    public void addSponsor(Sponsor sponsor) {
        this.sponsors.add(sponsor);
        sponsor.updateTeam(this);
    }
}
