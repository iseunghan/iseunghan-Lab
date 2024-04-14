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

    @ManyToOne
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
```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
public class Member_Eager_Team_Lazy_Test {
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

    @DisplayName("단일 팀을 조회하고, 멤버를 사용하지 않을 때 -> 1개의 쿼리가 나간다.(팀 조회하는 쿼리 1개)")
    @Test
    void find_One_Team_test() {
        clearPersistenceContext();

        System.out.println("----------find_One_Team_test start-----------");
        Team team = teamRepository.findTeamByName("team1")
                .orElseThrow(RuntimeException::new);
        assertThat(team.getName()).isEqualTo("team1");
        System.out.println("----------find_One_Team_test end-----------");
    }

    @DisplayName("모든 팀을 조회하고, 지연로딩 된 멤버를 사용할 때 -> N+1이 발생한다.(team1,2,3 조회하는 쿼리 1개, team1,2,3에 대한 멤버 조회하는 쿼리 3개)")
    @Test
    void team_findAll_test() {
        clearPersistenceContext();

        System.out.println("----------team_findAll_test start-----------");
        List<Team> teamList = teamRepository.findAll();
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

    @DisplayName("모든 멤버를 조회하면, EAGER 전략으로 팀을 조회하여 -> N+1이 발생한다.(모든 멤버 조회 1개, 각 팀을 조회하는 쿼리 3개)")
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
### find_One_Team_test()
**중요 로그:**  
LAZY 전략으로 로딩된 Member를 사용하지 않았으므로 Team을 조회하는 하나의 쿼리만 나간다.  
```console
----------find_One_Team_test start-----------
Hibernate: 
    select
        t1_0.id,
        t1_0.name 
    from
        team t1_0 
    where
        t1_0.name=?
----------find_One_Team_test end-----------
```

### team_findAll_test()
**중요 로그:**  
LAZY 전략: 팀을 조회하고, 멤버의 프로퍼티를 `*사용하는 시점에*` -> 멤버를 조회하는 쿼리가 발생한다.
```console
----------team_findAll_test start-----------
Hibernate: 
    select
        t1_0.id,
        t1_0.name 
    from
        team t1_0
----------team_findAll_test mid-----------
Hibernate: 
    select
        m1_0.team_id,
        m1_0.id,
        m1_0.name 
    from
        member m1_0 
    where
        m1_0.team_id=?
member1-1
member1-2
Hibernate: 
    select
        m1_0.team_id,
        m1_0.id,
        m1_0.name 
    from
        member m1_0 
    where
        m1_0.team_id=?
member2-1
member2-2
Hibernate: 
    select
        m1_0.team_id,
        m1_0.id,
        m1_0.name 
    from
        member m1_0 
    where
        m1_0.team_id=?
member3-1
member3-2
----------team_findAll_test end-----------
```  
팀을 조회했지만, 팀 내부에 있는 멤버를 조회하는 쿼리가 포함되어 N+1 쿼리가 발생한다.
이전에는 select m.id, m.name, m.team_id from member m where m.id = ? 라는 쿼리가 멤버 수만큼 나갔는데, 이번에 업데이트 되면서 FK로 검색하여 1개의 쿼리가 발생한다.

### member_findAll_test()
**중요 로그:**  
Member의 Team은 EAGER 전략으로 되어 있기 때문에 member를 조회하는 시점에 Team을 조회하는 쿼리가 같이 나간다.
실제 아래 로그에서도 Member의 Team.name 프로퍼티를 조회할 때 쿼리가 나가지 않았다.(1차캐시 사용)
```console
----------member_findAll_test start-----------
Hibernate: 
    select
        m1_0.id,
        m1_0.name,
        m1_0.team_id 
    from
        member m1_0
Hibernate: 
    select
        t1_0.id,
        t1_0.name 
    from
        team t1_0 
    where
        t1_0.id=?
Hibernate: 
    select
        t1_0.id,
        t1_0.name 
    from
        team t1_0 
    where
        t1_0.id=?
Hibernate: 
    select
        t1_0.id,
        t1_0.name 
    from
        team t1_0 
    where
        t1_0.id=?
----------member_findAll_test mid-----------
team1
team1
team2
team2
team3
team3
----------member_findAll_test end-----------
```
