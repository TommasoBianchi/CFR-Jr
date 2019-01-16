set Q1 ordered;
set Q2 ordered;
set Q3 ordered;

set H1 ordered;
set H2 ordered;
set H3 ordered;

# param U1{Q1,Q2,Q3} default 0;
# param U2{Q1,Q2,Q3} default 0;
# param U3{Q1,Q2,Q3} default 0;

param U1{Q1,Q2,Q3};
param U2{Q1,Q2,Q3};
param U3{Q1,Q2,Q3};

param F1{H1,Q1};
param f1{H1};
param F2{H2,Q2};
param f2{H2};
param F3{H3,Q3};
param f3{H3};

param suppU{Q1,Q2,Q3};

param p1_num default 0;
set P1 := 1 .. p1_num;
param p2_num default 0;
set P2 := 1 .. p2_num;
param p3_num default 0;
set P3 := 1 .. p3_num;

param rp1{P1,Q1} binary;
param rp2{P2,Q2} binary;
param rp3{P3,Q3} binary;

set P1P2P3 within P1 cross P2 cross P3 default {};

#################################PHASE I+II VARS
var sigma{P1P2P3} >= 0, <= 1;
var v1{H1};
var v2{H2};
var v3{H3};

#################################PHASE I AUXILIARY VARIABLES
var aux_c11 >= 0;
var aux_c12 >= 0;
var aux_c13 >= 0;
var slack_c21{Q1} >= 0;
var slack_c22{Q2} >= 0;
var slack_c23{Q3} >= 0;
var aux_c3 >= 0;

#################################PHASE I MASTER
minimize aux_obj:
	 aux_c11 + aux_c12 + aux_c13 + aux_c3;

s.t. c11_phase1:
     sum{(p1,p2,p3) in P1P2P3} sigma[p1,p2,p3] * sum{q1 in Q1,q2 in Q2, q3 in Q3}rp1[p1,q1]*rp2[p2,q2]*rp3[p3,q3]*U1[q1,q2,q3] + aux_c11 = sum{h1 in H1} v1[h1]*f1[h1];

s.t. c12_phase1:
     sum{(p1,p2,p3) in P1P2P3} sigma[p1,p2,p3] * sum{q1 in Q1,q2 in Q2, q3 in Q3}rp1[p1,q1]*rp2[p2,q2]*rp3[p3,q3]*U2[q1,q2,q3] + aux_c12 = sum{h2 in H2} v2[h2]*f2[h2];

s.t. c13_phase1:
     sum{(p1,p2,p3) in P1P2P3} sigma[p1,p2,p3] * sum{q1 in Q1,q2 in Q2, q3 in Q3}rp1[p1,q1]*rp2[p2,q2]*rp3[p3,q3]*U3[q1,q2,q3] + aux_c13 = sum{h3 in H3} v3[h3]*f3[h3];

s.t. c21_phase1{q1 in Q1}: #add support
     sum{(p1,p2,p3) in P1P2P3} sigma[p1,p2,p3] * (sum{q2 in Q2: rp2[p2,q2]==1} sum{q3 in Q3: rp3[p3,q3]==1} U1[q1,q2,q3]) + slack_c21[q1] - sum{h1 in H1} F1[h1,q1]*v1[h1] = 0;

s.t. c22_phase1{q2 in Q2}: #add support
     sum{(p1,p2,p3) in P1P2P3} sigma[p1,p2,p3] * (sum{q1 in Q1: rp1[p1,q1]==1} sum{q3 in Q3: rp3[p3,q3]==1} U2[q1,q2,q3]) + slack_c22[q2] - sum{h2 in H2} F2[h2,q2]*v2[h2] = 0;

s.t. c23_phase1{q3 in Q3}: #add support
     sum{(p1,p2,p3) in P1P2P3} sigma[p1,p2,p3] * (sum{q1 in Q1: rp1[p1,q1]==1} sum{q2 in Q2: rp2[p2,q2]==1} U3[q1,q2,q3]) + slack_c23[q3] - sum{h3 in H3} F3[h3,q3]*v3[h3] = 0;

s.t. c3_phase1:
     sum{(p1,p2,p3) in P1P2P3} sigma[p1,p2,p3] + aux_c3 = 1;


#################################PHASE II MASTER
# maximize welfare:
#      sum{(p1,p2,p3) in P1P2P3} sigma[p1,p2,p3]*sum{q1 in Q1,q2 in Q2,q3 in Q3}rp1[p1,q1]*rp2[p2,q2]*rp3[p3,q3]*(U1[q1,q2,q3]+U2[q1,q2,q3]+U3[q1,q2,q3]);

minimize welfare:
     - sum{(p1,p2,p3) in P1P2P3} sigma[p1,p2,p3]*sum{q1 in Q1,q2 in Q2,q3 in Q3}rp1[p1,q1]*rp2[p2,q2]*rp3[p3,q3]*(U1[q1,q2,q3]+U2[q1,q2,q3]+U3[q1,q2,q3]);

s.t. c11:
     sum{(p1,p2,p3) in P1P2P3} sigma[p1,p2,p3] * sum{q1 in Q1,q2 in Q2, q3 in Q3}rp1[p1,q1]*rp2[p2,q2]*rp3[p3,q3]*U1[q1,q2,q3] = sum{h1 in H1} v1[h1]*f1[h1];

s.t. c12:
     sum{(p1,p2,p3) in P1P2P3} sigma[p1,p2,p3] * sum{q1 in Q1,q2 in Q2, q3 in Q3}rp1[p1,q1]*rp2[p2,q2]*rp3[p3,q3]*U2[q1,q2,q3] = sum{h2 in H2} v2[h2]*f2[h2];

s.t. c13:
     sum{(p1,p2,p3) in P1P2P3} sigma[p1,p2,p3] * sum{q1 in Q1,q2 in Q2, q3 in Q3}rp1[p1,q1]*rp2[p2,q2]*rp3[p3,q3]*U3[q1,q2,q3] = sum{h3 in H3} v3[h3]*f3[h3];

s.t. c21{q1 in Q1}:
     sum{(p1,p2,p3) in P1P2P3} sigma[p1,p2,p3] * (sum{q2 in Q2: rp2[p2,q2]==1} sum{q3 in Q3: rp3[p3,q3]==1} U1[q1,q2,q3]) - sum{h1 in H1} F1[h1,q1]*v1[h1] <= 0;

s.t. c22{q2 in Q2}:
     sum{(p1,p2,p3) in P1P2P3} sigma[p1,p2,p3] * (sum{q1 in Q1: rp1[p1,q1]==1} sum{q3 in Q3: rp3[p3,q3]==1} U2[q1,q2,q3]) - sum{h2 in H2} F2[h2,q2]*v2[h2] <= 0;

s.t. c23{q3 in Q3}:
     sum{(p1,p2,p3) in P1P2P3} sigma[p1,p2,p3] * (sum{q1 in Q1: rp1[p1,q1]==1} sum{q2 in Q2: rp2[p2,q2]==1} U3[q1,q2,q3]) - sum{h3 in H3} F3[h3,q3]*v3[h3] <= 0;

s.t. c3:
     sum{(p1,p2,p3) in P1P2P3} sigma[p1,p2,p3] = 1;

################################PRICER vars and params
param alpha1;
param alpha2;
param alpha3;
param gamma;

param const_viol_part;
param violation;

param beta1{Q1};
param beta2{Q2};
param beta3{Q3};

var rp1_pricer{Q1} binary;
var rp2_pricer{Q2} binary;
var rp3_pricer{Q3} binary;

# per il quadratico
var z{Q1,Q2} >= 0, <= 1;

# per il cubico
/* var z_123{Q1,Q2,Q3} >= 0, <= 1;
var z_12{Q1,Q2}  >= 0, <= 1;
var z_13{Q1,Q3}  >= 0, <= 1;
var z_23{Q2,Q3}  >= 0, <= 1; */

################################ PRICER MILP
# minimize obj_pricer_milp:
#     sum{q1 in Q1, q2 in Q2, q3 in Q3} (
#         z_123[q1,q2,q3] * ((alpha1-1)*U1[q1,q2,q3] + (alpha2-1)*U2[q1,q2,q3] + (alpha3-1)*U3[q1,q2,q3])
#       ) + sum{q1 in Q1,q2 in Q2,q3 in Q3} beta1[q1]*z_23[q2,q3]*U1[q1,q2,q3] + sum{q1 in Q1,q2 in Q2,q3 in Q3} beta2[q2]*z_13[q1,q3]*U2[q1,q2,q3] + sum{q1 in Q1,q2 in Q2,q3 in Q3} beta3[q3]*z_12[q1,q2]*U3[q1,q2,q3];


# linearized
/* maximize obj_pricer_milp:
    sum{q1 in Q1, q2 in Q2, q3 in Q3} (
        z_123[q1,q2,q3] * ((alpha1+1)*U1[q1,q2,q3] + (alpha2+1)*U2[q1,q2,q3] + (alpha3+1)*U3[q1,q2,q3])
      ) + sum{q1 in Q1,q2 in Q2,q3 in Q3} beta1[q1]*z_23[q2,q3]*U1[q1,q2,q3] + sum{q1 in Q1,q2 in Q2,q3 in Q3} beta2[q2]*z_13[q1,q3]*U2[q1,q2,q3] + sum{q1 in Q1,q2 in Q2,q3 in Q3} beta3[q3]*z_12[q1,q2]*U3[q1,q2,q3]; */

# quadratic
maximize obj_pricer_milp:
		sum{q1 in Q1, q2 in Q2, q3 in Q3} (
			z[q1,q2]*rp3_pricer[q3]*((alpha1+1)*U1[q1,q2,q3] + (alpha2+1)*U2[q1,q2,q3] + (alpha3+1)*U3[q1,q2,q3])
			)+ sum{q1 in Q1,q2 in Q2,q3 in Q3} beta1[q1]* rp2_pricer[q2]*rp3_pricer[q3] *U1[q1,q2,q3] + sum{q1 in Q1,q2 in Q2,q3 in Q3} beta2[q2]* rp1_pricer[q1]*rp3_pricer[q3] *U2[q1,q2,q3] + sum{q1 in Q1,q2 in Q2,q3 in Q3} beta3[q3]* rp1_pricer[q1]*rp2_pricer[q2] *U3[q1,q2,q3];


# cubic
/* maximize obj_pricer_milp:
    sum{q1 in Q1, q2 in Q2, q3 in Q3} (
        rp1_pricer[q1]*rp2_pricer[q2]*rp3_pricer[q3] * ((alpha1+1)*U1[q1,q2,q3] + (alpha2+1)*U2[q1,q2,q3] + (alpha3+1)*U3[q1,q2,q3])
      ) + sum{q1 in Q1,q2 in Q2,q3 in Q3} beta1[q1]* rp2_pricer[q2]*rp3_pricer[q3] *U1[q1,q2,q3] + sum{q1 in Q1,q2 in Q2,q3 in Q3} beta2[q2]* rp1_pricer[q1]*rp3_pricer[q3] *U2[q1,q2,q3] + sum{q1 in Q1,q2 in Q2,q3 in Q3} beta3[q3]* rp1_pricer[q1]*rp2_pricer[q2] *U3[q1,q2,q3]; */

# linearized
# this is the objective function for the auxiliary game's pricer
/* maximize obj_pricer_milp_aux:
sum{q1 in Q1, q2 in Q2, q3 in Q3} (
        z_123[q1,q2,q3] * (alpha1*U1[q1,q2,q3] + alpha2*U2[q1,q2,q3] + alpha3*U3[q1,q2,q3])
      ) + sum{q1 in Q1,q2 in Q2,q3 in Q3} beta1[q1]*z_23[q2,q3]*U1[q1,q2,q3] + sum{q1 in Q1,q2 in Q2,q3 in Q3} beta2[q2]*z_13[q1,q3]*U2[q1,q2,q3] + sum{q1 in Q1,q2 in Q2,q3 in Q3} beta3[q3]*z_12[q1,q2]*U3[q1,q2,q3]; */

# quadratic
maximize obj_pricer_milp_aux:
    sum{q1 in Q1, q2 in Q2, q3 in Q3} (
        z[q1,q2]*rp3_pricer[q3] * (alpha1*U1[q1,q2,q3] + alpha2*U2[q1,q2,q3] + alpha3*U3[q1,q2,q3])
      ) + sum{q1 in Q1,q2 in Q2,q3 in Q3} beta1[q1]* rp2_pricer[q2]*rp3_pricer[q3] *U1[q1,q2,q3] + sum{q1 in Q1,q2 in Q2,q3 in Q3} beta2[q2]* rp1_pricer[q1]*rp3_pricer[q3] *U2[q1,q2,q3] + sum{q1 in Q1,q2 in Q2,q3 in Q3} beta3[q3]* rp1_pricer[q1]*rp2_pricer[q2] *U3[q1,q2,q3];

# cubic
/* maximize obj_pricer_milp_aux:
    sum{q1 in Q1, q2 in Q2, q3 in Q3} (
        rp1_pricer[q1]*rp2_pricer[q2]*rp3_pricer[q3] * (alpha1*U1[q1,q2,q3] + alpha2*U2[q1,q2,q3] + alpha3*U3[q1,q2,q3])
      ) + sum{q1 in Q1,q2 in Q2,q3 in Q3} beta1[q1]* rp2_pricer[q2]*rp3_pricer[q3] *U1[q1,q2,q3] + sum{q1 in Q1,q2 in Q2,q3 in Q3} beta2[q2]* rp1_pricer[q1]*rp3_pricer[q3] *U2[q1,q2,q3] + sum{q1 in Q1,q2 in Q2,q3 in Q3} beta3[q3]* rp1_pricer[q1]*rp2_pricer[q2] *U3[q1,q2,q3]; */


s.t. const1_milp_sf1{h1 in H1}:
    sum{q1 in Q1} F1[h1,q1]*rp1_pricer[q1] = f1[h1];

s.t. const2_milp_sf2{h2 in H2}:
    sum{q2 in Q2} F2[h2,q2]*rp2_pricer[q2] = f2[h2];

s.t. const3_milp_sf3{h3 in H3}:
    sum{q3 in Q3} F3[h3,q3]*rp3_pricer[q3] = f3[h3];

#
# constraints for the quadratic problem
#
s.t. quadratic_z_1{q1 in Q1, q2 in Q2}:
	z[q1,q2] <= rp1_pricer[q1];
s.t. quadratic_z_2{q1 in Q1, q2 in Q2}:
	z[q1,q2] <= rp2_pricer[q2];
s.t. quadratic_z_3{q1 in Q1, q2 in Q2}:
	z[q1,q2] >= rp1_pricer[q1] + rp2_pricer[q2] - 1;
#
# FULLY LINEARIZED
#
/* s.t. const4_milp_z12{q1 in Q1,q2 in Q2}:
	z_12[q1,q2] <= rp1_pricer[q1];

s.t. const5_milp_z12{q1 in Q1,q2 in Q2}:
	z_12[q1,q2] <= rp2_pricer[q2];

s.t. const6_milp_z12{q1 in Q1,q2 in Q2}:
	z_12[q1,q2] >= rp1_pricer[q1] + rp2_pricer[q2] - 1;

s.t. const7_milp_z13{q1 in Q1,q3 in Q3}:
	z_13[q1,q3] <= rp1_pricer[q1];

s.t. const8_milp_z13{q1 in Q1,q3 in Q3}:
	z_13[q1,q3] <= rp3_pricer[q3];

s.t. const9_milp_z13{q1 in Q1,q3 in Q3}:
	z_13[q1,q3] >= rp1_pricer[q1] + rp3_pricer[q3] - 1;

s.t. const10_milp_z23{q2 in Q2,q3 in Q3}:
	z_23[q2,q3] <= rp2_pricer[q2];

s.t. const11_milp_z23{q2 in Q2,q3 in Q3}:
	z_23[q2,q3] <= rp3_pricer[q3];

s.t. const12_milp_z23{q2 in Q2,q3 in Q3}:
	z_23[q2,q3] >= rp2_pricer[q2] + rp3_pricer[q3] - 1;

s.t. const13_milp_z123{q1 in Q1,q2 in Q2,q3 in Q3}:
	z_123[q1,q2,q3] <= z_12[q1,q2];

s.t. const14_milp_z123{q1 in Q1,q2 in Q2,q3 in Q3}:
	z_123[q1,q2,q3] <= rp3_pricer[q3];

s.t. const15_milp_z123{q1 in Q1,q2 in Q2,q3 in Q3}:
	z_123[q1,q2,q3] >= z_12[q1,q2] + rp3_pricer[q3] - 1; */


data;
