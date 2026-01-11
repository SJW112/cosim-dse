%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Code to Arrange power flow data of the grid for state estimation
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [PowerData]=PowerDData(GridData,IEEE13)
%     eval(name_of_model);
    %*******************************************************************
    % sample grid power : IEEE 13
    V_all=IEEE13.V_all;
    P_all=IEEE13.P_all;
    Q_all=IEEE13.Q_all;
    I_all=IEEE13.I_all;

    V_all=V_all.V;
    P_all=P_all.P;
    I_all=I_all.I;
    Q_all=Q_all.Q;
    base_voltage =[4160*sqrt(3)*9*(ones(3,1));(4160/sqrt(3))*(ones(9,1));(480/sqrt(3))*(ones(3,1));(4160/sqrt(3))*(ones(33,1))];
    V_all=V_all(:,1);
    P_all=P_all(:,1);
    Q_all=Q_all(:,1);
    Q_all=Q_all(:,1);

    V_all=insert_missing_phases(V_all(:,1));
    I_all=insert_missing_phases(I_all(:,1));
    P_all=insert_missing_phases(P_all(:,1));
    Q_all=insert_missing_phases(Q_all(:,1));
    V_all=V_all./base_voltage;

    % V_all(1:3)=[];
    % I_all(1:3)=[]; 
    % P_all(1:3)=[]; 
    % Q_all(1:3)=[];


    Vmagn=abs(V_all);
    Vph=angle(V_all);

    V_magn=reshape(Vmagn,3,[]);
    V_ph=reshape(Vph,3,[]);
    Pinj=reshape(P_all,3,[]);
    Qinj=reshape(Q_all,3,[]);
    Amps=reshape(I_all,3,[]);
    base_power = 1e8;
    % GridData.base_current = base_power./2400;
    GridData.base_current = base_power./base_voltage;
    PowerData=struct;
    PowerData.Pinj=Pinj./base_power;
    PowerData.Qinj=Qinj./base_power;
    PowerData.Vmagn=V_magn;
    PowerData.Vph=V_ph;

    Volts=reshape(V_all,3,[]);

% once the solution of the PF is found, the struct PowerData is
% populated with the data that later will be given to the state
% estimator
for m=1:GridData.Lines_num %the assumption is that all power flows are calculated at the end of the lines
    PowerData.Pflow(:,m)=real(Volts(:,GridData.topology(3,m)).*conj(Amps(:,m)));
    PowerData.Qflow(:,m)=imag(Volts(:,GridData.topology(3,m)).*conj(Amps(:,m)));
end

PowerData.Vph = wrapToPi(PowerData.Vph);
PowerData.Imagn=abs(Amps);
PowerData.Iph(1,:)=wrapToPi(phase(Amps(1,:)));
PowerData.Iph(2,:)=wrapToPi(phase(Amps(2,:)));
PowerData.Iph(3,:)=wrapToPi(phase(Amps(3,:)));
end

