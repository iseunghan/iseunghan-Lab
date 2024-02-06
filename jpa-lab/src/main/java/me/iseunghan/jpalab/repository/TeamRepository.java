package me.iseunghan.jpalab.repository;

import me.iseunghan.jpalab.entity.Team;
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

    @EntityGraph(attributePaths = "members")
    @Query(value = "select t from Team t where t.name = :name")
    Optional<Team> findTeamByNameEntityGraph(String name);

    @EntityGraph(attributePaths = "members")
    @Query(value = "select t from Team t")
    List<Team> findTeamsEntityGraph();
}
