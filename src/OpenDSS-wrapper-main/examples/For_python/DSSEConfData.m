%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Code to generate the parameters for the testing of the state estimator,
% the structure with the information of the measurements available and the
% structure with the accuracies of those measurements

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function [Test_SetUp,Combination_devices,Accuracy] =DSSEConfData(GridData)
% structure with parameters for the testing of the state estimator
Test_SetUp = struct;
Test_SetUp.N_MC = 1500; %number of MC simulation, for reliable results set between 1000 and 10 000
Test_SetUp.limit1 = 0.000001; %treshold accuracy to interrupt newton rapson
Test_SetUp.limit2 = 50; %maximum number of iterations
Test_SetUp.time_steps = 1; %number of time step in each MC simulation
% Combination_P = [3,5]; 
% Combination_Q = [3,5]; 
% Combination_P = 1:(GridData.Nodes_num); 
% Combination_Q = 1:(GridData.Nodes_num);

Combination_P = [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]; 
Combination_Q = [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16];
% Combination_Pseudo =  2:(GridData.Nodes_num);
Combination_Pseudo =  [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16];

% Combination_Vmagn =   1:(GridData.Nodes_num);% 1:GridData.Nodes_num
% Combination_Vph =     1:(GridData.Nodes_num);
% Combination_Vmagn =   1:(GridData.Nodes_num);% 1:GridData.Nodes_num
% Combination_Vph =     1:(GridData.Nodes_num); 
Combination_Vmagn =   [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16];% 1:GridData.Nodes_num
Combination_Vph =     [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]; 

Combination_Imagn =   []; %1:GridData.Lines_num
Combination_Iph =     []; 
Combination_Pflow =   []; 
Combination_Qflow =   [];

% here the uncertainty of devices and pseudo measurements is indicated
unc_dev = 0.01/3;
unc_pseudo = 0.5/3;
%the structure with the information of the measurements available
Combination_devices=struct;
Combination_devices.Combination_P = Combination_P;
Combination_devices.Combination_Q = Combination_Q;
Combination_devices.Combination_Vmagn = Combination_Vmagn;
Combination_devices.Combination_Vph = Combination_Vph;
Combination_devices.Combination_Imagn = Combination_Imagn;
Combination_devices.Combination_Iph = Combination_Iph;
Combination_devices.Combination_Pflow = Combination_Pflow;
Combination_devices.Combination_Qflow = Combination_Qflow;
Combination_devices.Combination_Pseudo = Combination_Pseudo;

%the accuracy for each class of device is assigned
Accuracy_P = sqrt(2*unc_dev^2); %accuracy of active power injection measurement
Accuracy_Q = sqrt(2*unc_dev^2); %accuracy of active power injection measurement
Accuracy_Vmagn = unc_dev; %accuracy of active power injection measurement
Accuracy_Vph = unc_dev; %accuracy of active power injection measurement)
Accuracy_Imagn = unc_dev; %branches with voltage phase angle measurement
Accuracy_Iph = unc_dev; %branches with voltage phase angle measurement
Accuracy_Pflow = sqrt(2*unc_dev^2); %branches with voltage phase angle measurement
Accuracy_Qflow = sqrt(2*unc_dev^2); %branches with voltage phase angle measurement
Accuracy_pseudo = unc_pseudo;
%structure with the accuracies of the measurements
Accuracy=struct;
Accuracy.Accuracy_P=Accuracy_P;
Accuracy.Accuracy_Q=Accuracy_Q;
Accuracy.Accuracy_Vmagn=Accuracy_Vmagn;
Accuracy.Accuracy_Vph=Accuracy_Vph;
Accuracy.Accuracy_Imagn=Accuracy_Imagn;
Accuracy.Accuracy_Iph=Accuracy_Iph;
Accuracy.Accuracy_Pflow=Accuracy_Pflow;
Accuracy.Accuracy_Qflow=Accuracy_Qflow;
Accuracy.Accuracy_pseudo=Accuracy_pseudo;

Pseudo_measure=zeros(1,GridData.Nodes_num);
P_measure=zeros(1,GridData.Nodes_num);
Q_measure=zeros(1,GridData.Nodes_num);
Vmagn_measure=zeros(1,GridData.Nodes_num);
Vph_measure=zeros(1,GridData.Nodes_num);
Imagn_measure=zeros(1,GridData.Lines_num);
Iph_measure=zeros(1,GridData.Lines_num);
Pflow_measure=zeros(1,GridData.Lines_num);
Qflow_measure=zeros(1,GridData.Lines_num);
% in this loop we create a structure to better organize the measurements
% for the next functions
for n=1:GridData.Nodes_num
    if isempty(Combination_P)==0
        if  sum(ismember(Combination_P(1,:),n)) >0
            P_measure(1,n) = 1;
        end
    end
    if isempty(Combination_Q)==0
        if  sum(ismember(Combination_Q(1,:),n)) >0
            Q_measure(1,n)=1;
        end
    end
    if isempty(Combination_Pseudo)==0
        if  sum(ismember(Combination_Pseudo(1,:),n)) >0
            Pseudo_measure(1,n)=1;
        end
    end
    if isempty(Combination_Vmagn)==0
        if sum(ismember(Combination_Vmagn(1,:),n)) >0
            Vmagn_measure(1,n) = 1;
        end
    end
    if isempty(Combination_Vph)==0
        if sum(ismember(Combination_Vph(1,:),n)) >0
            Vph_measure(1,n)=1;
        end
    end
end

for m=1:GridData.Lines_num
    if isempty(Combination_Imagn)==0
        if sum(ismember(Combination_Imagn(1,:),m)) >0
            Imagn_measure(1,m)=1;
        end
    end
    if isempty(Combination_Iph)==0
        if sum(ismember(Combination_Iph(1,:),m)) >0
            Iph_measure(1,m)=1;
        end
    end
    if isempty(Combination_Pflow)==0
        if sum(ismember(Combination_Pflow(1,:),m)) >0
            Pflow_measure(1,m)=1;
        end
    end
    if isempty(Combination_Qflow)==0
        if sum(ismember(Combination_Qflow(1,:),m)) >0
            Qflow_measure(1,m)=1;
        end
    end
end

Combination_devices.P_measure = [P_measure;zeros(size(P_measure))];
Combination_devices.Q_measure = [Q_measure;zeros(size(Q_measure))];
Combination_devices.Vmagn_measure = [Vmagn_measure;zeros(size(Vmagn_measure))];
Combination_devices.Vph_measure = [Vph_measure;zeros(size(Vph_measure))];
Combination_devices.Imagn_measure = [Imagn_measure;zeros(size(Imagn_measure))];
Combination_devices.Iph_measure = [Iph_measure;zeros(size(Iph_measure))];
Combination_devices.Pflow_measure = [Pflow_measure;zeros(size(Pflow_measure))];
Combination_devices.Qflow_measure = [Qflow_measure;zeros(size(Qflow_measure))];
Combination_devices.Pseudo_measure = [Pseudo_measure;zeros(size(Pseudo_measure))];
end
