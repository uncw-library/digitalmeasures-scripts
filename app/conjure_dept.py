from globals import ACADEMIC_AFFAIRS, COLL_DEPT


def conjure_coll_dept_assignment(parsed_user):
    # Users are not entering accurate data.
    # There is no dept of Randall Library within the college of Business.
    # This magic wand is only necessary while the digitalmeasure data is incorrect.
    dmd_depts = parsed_user.get("current_depts")
    college_depts_info = [
        match_college(dept) for dept in dmd_depts if (dept and match_college(dept))
    ]
    return college_depts_info


def match_college(dept):
    # because users entered the wrong college for their dept in 10% of files
    # we have to assume they got the dept correct, and manually lookup the coll.
    # we also hardcoded the uid for college & for dept, for consistency
    for coll, bundle in COLL_DEPT.items():
        if dept in bundle.get("depts"):
            return {
                "coll_name": coll,
                "coll_uid": bundle["uid"],
                "dept_name": dept,
                "dept_uid": bundle["depts"][dept],
            }
    # if dept not in COLL_DEPT, check if it's in Academic Affairs
    if dept in ACADEMIC_AFFAIRS.get("depts"):
        return {
            "coll_name": ACADEMIC_AFFAIRS["name"],
            "coll_uid": ACADEMIC_AFFAIRS["uid"],
            "dept_name": dept,
            "dept_uid": ACADEMIC_AFFAIRS["depts"][dept],
        }
    return None
