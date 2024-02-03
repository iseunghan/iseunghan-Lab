## Abstract
**Team - Member 연관관계**
- Team의 member는 OneToMany(LAZY) 전략 사용
- Member의 Team은 ManyToOne(EAGER) 전략 사용

## Domain
### Team
```java
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Entity
public class Team {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;

    @OneToMany(mappedBy = "team", fetch = FetchType.LAZY, cascade = CascadeType.ALL)
    private List<Member> members = new ArrayList<>();

    @Builder
    private Team(String name) {
        this.name = name;
    }

    public void addMember(Member member) {
        this.members.add(member);
        member.updateTeam(this);
    }
}


```

### Member
```java
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Entity
public class Member {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "TEAM_ID")
    private Team team;

    @Builder
    private Member(String name) {
        this.name = name;
    }

    public void updateTeam(Team team) {
        this.team = team;
    }
}

```

## Test
[Member_Eager_Team_Lazy.md](Member_Eager_Team_Lazy.md)와 동일 (member_findAll_test의 DisplayName만 다름)
```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
public class Member_Lazy_Team_Lazy_Test {
    @Autowired private MemberRepository memberRepository;
    @Autowired private TeamRepository teamRepository;
    @PersistenceContext private EntityManager em;

    // setup, clear, clearPersistenceContext 메소드 동일

    ...

    @DisplayName("모든 멤버를 조회하고, 지연로딩 된 팀을 사용할 때 -> N+1이 발생한다.(모든 멤버 조회 1개, 각 팀을 조회하는 쿼리 3개)") // 이것만 다름!
    @Test
    void member_findAll_test() {
        clearPersistenceContext();

        System.out.println("----------member_findAll_test start-----------");
        List<Member> memberList = memberRepository.findAll();
        assertThat(memberList).hasSize(6);
        System.out.println("----------member_findAll_test mid-----------");
        memberList.stream()
                .map(Member::getTeam)
                .map(Team::getName)
                .forEach(System.out::println);
        System.out.println("----------member_findAll_test end-----------");
    }
}

```

## Console output
### member_findAll_test()
**중요 로그:**  
Member의 Team은 LAZY 전략으로 되어 있기 때문에 member를 조회하는 시점에는 member 조회 쿼리만 나가고, 실제 Team을 사용할 때 Team을 조회하는 쿼리가 나간다.
실제 아래 로그에서도 `----------member_findAll_test mid-----------` 이후로 Team을 조회하는 쿼리가 나가는 것을 확인할 수 있다.
```console
----------member_findAll_test start-----------
Hibernate: 
    select
        m1_0.id,
        m1_0.name,
        m1_0.team_id 
    from
        member m1_0
----------member_findAll_test mid-----------
Hibernate: 
    select
        t1_0.id,
        t1_0.name 
    from
        team t1_0 
    where
        t1_0.id=?
team1
team1
Hibernate: 
    select
        t1_0.id,
        t1_0.name 
    from
        team t1_0 
    where
        t1_0.id=?
team2
team2
Hibernate: 
    select
        t1_0.id,
        t1_0.name 
    from
        team t1_0 
    where
        t1_0.id=?
team3
team3
----------member_findAll_test end-----------
```
