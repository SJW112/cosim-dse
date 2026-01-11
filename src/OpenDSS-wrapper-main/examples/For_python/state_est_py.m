    
   %% functions
   % Three_phase
   % Griddata
   % Powerddata
   % DSSEConfData
   % Weightm
   % calc_Mvector_external
   % VRIDSSE
   % Jacobian_m_VRIDSSE
   % calc_Mvector
   % calc_hx_VRIDSSE
   
%%

function [Vmag,Vph]=state_est_py(P,Q,V,I,Y)
   %%
   P=load('P.mat');
   Q=load('Q.mat');
   V=load('V.mat');
   I=load('I.mat');
   Y=load('Y.mat');
   



    IEEE13=struct;
    IEEE13.P_all=P;
    IEEE13.Q_all=Q;
    IEEE13.V_all=V;
    IEEE13.I_all=I;
    IEEE13.Y=Y;

    [Vmag,Vph]=Three_phase(IEEE13)

    

% end
