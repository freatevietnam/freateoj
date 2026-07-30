from collections import defaultdict

from django.db.models import Max

from judge.models import Profile, Submission


def common_solved_problems(profile_a, profile_b):
    a_solved = set(
        Submission.objects.filter(user=profile_a, points__gt=0, problem__is_public=True)
        .values_list('problem_id', flat=True).distinct()
    )
    b_solved = set(
        Submission.objects.filter(user=profile_b, points__gt=0, problem__is_public=True)
        .values_list('problem_id', flat=True).distinct()
    )
    return a_solved & b_solved


def head_to_head(profile_a, profile_b, common_ids):
    a_best = _best_scores(profile_a, common_ids)
    b_best = _best_scores(profile_b, common_ids)
    a_wins = b_wins = ties = 0
    for pid in common_ids:
        sa = a_best.get(pid, 0)
        sb = b_best.get(pid, 0)
        if sa > sb:
            a_wins += 1
        elif sb > sa:
            b_wins += 1
        else:
            ties += 1
    return {'a_wins': a_wins, 'b_wins': b_wins, 'ties': ties}


def _best_scores(profile, problem_ids):
    scores = Submission.objects.filter(
        user=profile, problem_id__in=problem_ids, points__gt=0
    ).values('problem_id').annotate(best=Max('points'))
    return {s['problem_id']: s['best'] for s in scores}


def topic_differential(profile_a, profile_b):
    from judge.models import ProblemGroup
    a_by_group = _solved_by_group(profile_a)
    b_by_group = _solved_by_group(profile_b)
    all_groups = set(a_by_group.keys()) | set(b_by_group.keys())
    result = []
    for gid in sorted(all_groups):
        ac = a_by_group.get(gid, 0)
        bc = b_by_group.get(gid, 0)
        group = ProblemGroup.objects.get(id=gid)
        diff = ac - bc
        total = max(ac, bc, 1)
        result.append({
            'group_name': group.full_name,
            'a_solved': ac,
            'b_solved': bc,
            'diff': diff,
            'pct': round((diff / total) * 100),
            'leader': 'a' if diff > 0 else 'b' if diff < 0 else 'tie',
        })
    return result


def _solved_by_group(profile):
    from django.db.models import Count
    return dict(
        Submission.objects.filter(user=profile, points__gt=0, problem__is_public=True)
        .values('problem__group_id')
        .annotate(cnt=Count('id', distinct=True))
        .values_list('problem__group_id', 'cnt')
    )
