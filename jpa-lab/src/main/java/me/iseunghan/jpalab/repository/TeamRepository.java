package me.iseunghan.jpalab.repository;

import me.iseunghan.jpalab.entity.Team;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;
import java.util.Optional;

public interface TeamRepository extends JpaRepository<Team, Long> {
    Optional<Team> findTeamByName(String name);

    @Query(value = "select t from Team t join fetch t.members where t.name = :name")
    Optional<Team> findTeamByNameFetchJoin(String name);

    @Query(value = "select t from Team t join fetch t.members")
    List<Team> findTeamsFetchJoin();

    @Query(
            value = "select t from Team t join fetch t.members",
            countQuery = "select count(t) from Team t"
    )
    List<Team> findTeamsFetchJoin(Pageable pageable);

    @Query(
            value = "select t from Team t",
            countQuery = "select count(t) from Team t"
    )
    Page<Team> findTeamsWithoutFetchJoin(Pageable pageable);

    @EntityGraph(attributePaths = "members")
    @Query(value = "select t from Team t where t.name = :name")
    Optional<Team> findTeamByNameEntityGraph(String name);

    @EntityGraph(attributePaths = "members")
    @Query(value = "select t from Team t")
    List<Team> findTeamsEntityGraph();

    @EntityGraph(attributePaths = "members")
    @Query(
            value = "select t from Team t",
            countQuery = "select count(t) from Team t"
    )
    List<Team> findTeamsEntityGraph(Pageable pageable);
}
