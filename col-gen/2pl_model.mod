set Q1 ordered;
set Q2 ordered;

set H1 ordered;
set H2 ordered;

# param U1{Q1,Q2} default 0;
# param U2{Q1,Q2} default 0;

param U1{Q1,Q2};
param U2{Q1,Q2};

param F1{H1,Q1};
param f1{H1};
param F2{H2,Q2};
param f2{H2};

param suppU{Q1,Q2};

param p1_num default 0;
set P1 := 1 .. p1_num;
param p2_num default 0;
set P2 := 1 .. p2_num;

param rp1{P1,Q1} binary;
param rp2{P2,Q2} binary;

set P1P2 within P1 cross P2 default {};

#################################PHASE I+II VARS
var sigma{P1P2} >= 0, <= 1;
var v1{H1};
var v2{H2};

#################################PHASE I AUXILIARY VARIABLES
var aux_c11 >= 0;
var aux_c12 >= 0;
var slack_c21{Q1} >= 0;
var slack_c22{Q2} >= 0;
var aux_c3 >= 0;

#################################PHASE I MASTER
minimize aux_obj:
	 aux_c11 + aux_c12 + aux_c3;

s.t. c11_phase1:
     sum{(p1,p2) in P1P2} sigma[p1,p2] * sum{q1 in Q1,q2 in Q2}rp1[p1,q1]*rp2[p2,q2]*U1[q1,q2] + aux_c11 = sum{h1 in H1} v1[h1]*f1[h1];

s.t. c12_phase1:
     sum{(p1,p2) in P1P2} sigma[p1,p2] * sum{q1 in Q1,q2 in Q2}rp1[p1,q1]*rp2[p2,q2]*U2[q1,q2] + aux_c12 = sum{h2 in H2} v2[h2]*f2[h2];

s.t. c21_phase1{q1 in Q1}: #add support
     sum{(p1,p2) in P1P2} sigma[p1,p2]*sum{q2 in Q2: rp2[p2,q2]==1} U1[q1,q2] + slack_c21[q1] - sum{h1 in H1} F1[h1,q1]*v1[h1] = 0;

s.t. c22_phase1{q2 in Q2}: #add support
     sum{(p1,p2) in P1P2} sigma[p1,p2]*sum{q1 in Q1:rp1[p1,q1]==1} U2[q1,q2] + slack_c22[q2] - sum{h2 in H2} F2[h2,q2]*v2[h2] = 0;

s.t. c3_phase1:
     sum{(p1,p2) in P1P2} sigma[p1,p2] + aux_c3 = 1;


#################################PHASE II MASTER
# maximize welfare:
#      sum{(p1,p2) in P1P2} sigma[p1,p2]*sum{q1 in Q1,q2 in Q2}rp1[p1,q1]*rp2[p2,q2]*(U1[q1,q2]+U2[q1,q2]);

minimize welfare:
     - sum{(p1,p2) in P1P2} sigma[p1,p2]*sum{q1 in Q1,q2 in Q2}rp1[p1,q1]*rp2[p2,q2]*(U1[q1,q2]+U2[q1,q2]);

s.t. c11:
     sum{(p1,p2) in P1P2} sigma[p1,p2] * sum{q1 in Q1,q2 in Q2}rp1[p1,q1]*rp2[p1,q2]*U1[q1,q2] = sum{h1 in H1} v1[h1]*f1[h1];

s.t. c12:
     sum{(p1,p2) in P1P2} sigma[p1,p2] * sum{q1 in Q1,q2 in Q2}rp1[p1,q1]*rp2[p2,q2]*U2[q1,q2] = sum{h2 in H2} v2[h2]*f2[h2];

s.t. c21{q1 in Q1}:
     sum{(p1,p2) in P1P2} sigma[p1,p2]*sum{q2 in Q2: rp2[p2,q2]==1} U1[q1,q2] - sum{h1 in H1} F1[h1,q1]*v1[h1] <= 0;

s.t. c22{q2 in Q2}:
     sum{(p1,p2) in P1P2} sigma[p1,p2]*sum{q1 in Q1: rp1[p1,q1]==1} U2[q1,q2] - sum{h2 in H2} F2[h2,q2]*v2[h2] <= 0;

s.t. c3:
     sum{(p1,p2) in P1P2} sigma[p1,p2] = 1;

################################PRICER---shared part
param alpha1;
param alpha2;
param gamma;

param const_viol_part;
param violation;

################################ PRICER (FOR ENUMERATION)---p1 part
param beta2{Q2};
param q1_ell symbolic in Q1;

var rp1_pricer{Q1} binary;

# minimize obj_pricer_p1:
maximize obj_pricer_p1:
	 sum{q2 in Q2} sum{q1 in Q1} beta2[q2] * rp1_pricer[q1]*U2[q1,q2];

s.t. const1_p1{h1 in H1}:
     sum{q1 in Q1} F1[h1,q1]*rp1_pricer[q1] = f1[h1];

s.t. const2_p1:
     rp1_pricer[q1_ell] =1;

################################ PRICER (FOR ENUMERATION)---p2 part
param beta1{Q1};
param q2_ell symbolic in Q2;

var rp2_pricer{Q2} binary;

# minimize obj_pricer_p2:
maximize obj_pricer_p2:
	 sum{q1 in Q1} sum{q2 in Q2} beta1[q1] * rp2_pricer[q2] * U1[q1,q2];

s.t. const1_p2{h2 in H2}:
     sum{q2 in Q2} F2[h2,q2]*rp2_pricer[q2] = f2[h2];

s.t. const2_p2:
     rp2_pricer[q2_ell] = 1;

################################ PRICER MILP
# - If the realization plans are binary variables (as we do here) the use of binary variables over leafs (z) is redundant.
# - The use of binary realization plans allows the use of the same pricer for both games with 2 pl and games with 2 pl and Nature.
# - Using unconstrained realization plans and binary variables over terminal nodes would reduce the number of binary variables, but in practice
# it would require two further steps: A) ensuring the resulting realization plans are pure, and B) adapting the algorithm to the 2pl+Nature setting
################################
# minimize obj_pricer_milp:
#     sum{q1 in Q1, q2 in Q2} (
#         rp1_pricer[q1] * rp2_pricer[q2] * ((alpha1-1)*U1[q1,q2] + (alpha2-1)*U2[q1,q2])
#       ) + sum{q2 in Q2} sum{q1 in Q1} beta2[q2] * rp1_pricer[q1]*U2[q1,q2] + sum{q1 in Q1} sum{q2 in Q2} beta1[q1] * rp2_pricer[q2] * U1[q1,q2];

maximize obj_pricer_milp:
    sum{q1 in Q1, q2 in Q2} (
        rp1_pricer[q1] * rp2_pricer[q2] * ((alpha1+1)*U1[q1,q2] + (alpha2+1)*U2[q1,q2])
      ) + sum{q2 in Q2} sum{q1 in Q1} beta2[q2] * rp1_pricer[q1]*U2[q1,q2] + sum{q1 in Q1} sum{q2 in Q2} beta1[q1] * rp2_pricer[q2] * U1[q1,q2];

# this is the objective function for the auxiliary game's pricer
# the difference is that there is no term r_1^T(U_1+U_2)r_2
maximize obj_pricer_milp_aux:
sum{q1 in Q1, q2 in Q2} (
     rp1_pricer[q1] * rp2_pricer[q2] * (alpha1*U1[q1,q2] + alpha2*U2[q1,q2])
  ) + sum{q2 in Q2} sum{q1 in Q1} beta2[q2] * rp1_pricer[q1]*U2[q1,q2] + sum{q1 in Q1} sum{q2 in Q2} beta1[q1] * rp2_pricer[q2] * U1[q1,q2];

s.t. const1_milp_sf1{h1 in H1}:
    sum{q1 in Q1} F1[h1,q1]*rp1_pricer[q1] = f1[h1];

s.t. const2_milp_sf2{h2 in H2}:
    sum{q2 in Q2} F2[h2,q2]*rp2_pricer[q2] = f2[h2];


data;
