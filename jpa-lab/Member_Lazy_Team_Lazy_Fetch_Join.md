## Abstract
**Team - Member 연관관계**
- Team의 member는 OneToMany(LAZY) 전략 사용
- Member의 Team은 ManyToOne(LAZY) 전략 사용

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

### Repository
각 Repository에 Fetch Join을 추가
```java
public interface MemberRepository extends JpaRepository<Member, Long> {
    @Query(value = "select m from Member m join fetch m.team")
    List<Member> findMembersFetchJoin();
}
```  
```java
public interface TeamRepository extends JpaRepository<Team, Long> {
    Optional<Team> findTeamByName(String name);
    @Query(value = "select t from Team t join fetch t.members where t.name = :name")
    Optional<Team> findTeamByNameFetchJoin(String name);
    @Query(value = "select t from Team t join fetch t.members")
    List<Team> findTeamsFetchJoin();
}
```

## Test
[Member_Eager_Team_Lazy.md](Member_Eager_Team_Lazy.md)의 setup, clear, clearPersistenceContext 메소드 동일
```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
public class Member_Lazy_Team_Lazy_Fetch_Join_Test {
    @Autowired private MemberRepository memberRepository;
    @Autowired private TeamRepository teamRepository;
    @PersistenceContext private EntityManager em;

    // setup, clear, clearPersistenceContext 메소드 동일 

    @DisplayName("단일 팀을 조회하고, 멤버를 사용하던 안하던 -> 1개의 쿼리가 나간다.(팀 조회하는 쿼리 1개)")
    @Test
    void find_One_Team_test() {
        clearPersistenceContext();

        System.out.println("----------find_One_Team_test start-----------");
        Team team = teamRepository.findTeamByNameFetchJoin("team1")
                .orElseThrow(RuntimeException::new);
        assertThat(team.getName()).isEqualTo("team1");
        System.out.println("----------find_One_Team_test end-----------");
    }

    @DisplayName("모든 팀을 조회하고, 지연로딩 된 멤버를 사용할 때 -> 단 1개의 쿼리만 나간다")
    @Test
    void team_findAll_test() {
        clearPersistenceContext();

        System.out.println("----------team_findAll_test start-----------");
        List<Team> teamList = teamRepository.findTeamsFetchJoin();
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

    @DisplayName("모든 멤버를 조회하고, 지연로딩 된 팀을 사용할 때 -> 단 1개의 쿼리만 나간다")
    @Test
    void member_findAll_test() {
        clearPersistenceContext();

        System.out.println("----------member_findAll_test start-----------");
        List<Member> memberList = memberRepository.findMembersFetchJoin();
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
Fetch Join으로 가져왔으므로 N+1 해결은 member를 사용하던 안하던 쿼리가 발생하지 않는다.
```console
----------find_One_Team_test start-----------
Hibernate: 
    select
        t1_0.id,
        m1_0.team_id,
        m1_0.id,
        m1_0.name,
        t1_0.name 
    from
        team t1_0 
    join
        member m1_0 
            on t1_0.id=m1_0.team_id 
    where
        t1_0.name=?
----------find_One_Team_test end-----------
```

### team_findAll_test()
**중요 로그:**  
Fetch Join으로 가져왔으므로 N+1 해결은 물론 사용하는 시점에 쿼리가 발생하지 않는다.
```console
----------team_findAll_test start-----------
Hibernate: 
    select
        t1_0.id,
        m1_0.team_id,
        m1_0.id,
        m1_0.name,
        t1_0.name 
    from
        team t1_0 
    join
        member m1_0 
            on t1_0.id=m1_0.team_id
----------team_findAll_test mid-----------
member1-1
member1-2
member2-1
member2-2
member3-1
member3-2
----------team_findAll_test end-----------
```  

### member_findAll_test()
**중요 로그:**  
member를 조회할 때 team을 fetch Join으로 불러왔기 때문에 inner join을 사용해서 한방에 가져왔다.
```console
----------member_findAll_test start-----------
Hibernate: 
    select
        m1_0.id,
        m1_0.name,
        t1_0.id,
        t1_0.name 
    from
        member m1_0 
    join
        team t1_0 
            on t1_0.id=m1_0.team_id
----------member_findAll_test mid-----------
team1
team1
team2
team2
team3
team3
----------member_findAll_test end-----------
```

