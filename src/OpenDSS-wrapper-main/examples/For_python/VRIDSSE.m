%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Voltage Real Imaginary Distribution System State Estimator (VRIDSSE)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function   [Vmagn_status,Vph_status] = VRIDSSE(PowerData,W,GridData,Test_SetUp)
% Jacobian matrix
[H] = Jacobian_m_VRIDSSE(GridData);
dre=size(H)
ruy=size(W)
HW = H'*W;
G1 = HW*H; %gain matrix
G2 = G1;
if GridData.inj_status
    G2(:,11*GridData.DM.NGF+10*GridData.DM.NGS+2*GridData.DM.Nload+1)=[];
    G2(11*GridData.DM.NGF+10*GridData.DM.NGS+2*GridData.DM.Nload+1,:)=[];
    for x = 1 : 11*GridData.DM.NGF + 10*GridData.DM.NGS + 2*GridData.DM.Nload + 2*GridData.Lines_num
        G2(:,x) = G2(:,x) .* ([GridData.base_status; GridData.base_current*ones(2*GridData.Lines_num,1)].^-1);
    end
    for x = 1 : 11*GridData.DM.NGF + 10*GridData.DM.NGS + 2*GridData.DM.Nload + 2*GridData.Lines_num
        G2(x,:) = G2(x,:) .* ([GridData.base_status; GridData.base_current*ones(2*GridData.Lines_num,1)].^-1)';
    end
end
P_post = inv(G2); %estimated state error covariance

%we initialize the state 
if strcmp(GridData.type_of_model,'single_phase')==1
    Vmagn_status=ones(GridData.Nodes_num,1);
    Vph_status=zeros(GridData.Nodes_num,1);
elseif strcmp(GridData.type_of_model,'three_phase_sequence')==1  || strcmp(GridData.type_of_model,'three_phase_unbalance')==1
    Vmagn_status=ones(3,GridData.Nodes_num);
    Vph_status=zeros(3,GridData.Nodes_num);
    Vph_status(2,:)=(4/3)*pi;
    Vph_status(3,:)=(2/3)*pi;
end
if GridData.inj_status == 1 %in case we consider dynamic measuremetns
    inj_status =  zeros(11*GridData.DM.NGF+10*GridData.DM.NGS + 2*GridData.DM.Nload,1);
else
    inj_status = 0;
end
 
max_delta=10; %dummy inizialitazion
iteration=0;

% Newton Rapson calculation of the state
while max_delta > 1e-12 &&  iteration < Test_SetUp.limit2
    iteration=iteration+1;
    [Meas_vector] = calc_Mvector(GridData,PowerData);% 1) Update vector of measurements based on the voltage estimated
    [hx] = calc_hx_VRIDSSE(Vmagn_status,Vph_status,GridData,inj_status); % 2) Calculate h(x) vector 
    res = Meas_vector-hx;    % build the residual vector
    HWres = HW*res;
    delta = G1\HWres;
    
    n = 1;
    if GridData.inj_status  == 1 %in case we consider dynamic status of the injection
        inj_status = inj_status + delta(1:11*GridData.DM.NGF+10*GridData.DM.NGS + 2*GridData.DM.Nload) ;
        n = 11*GridData.DM.NGF+10*GridData.DM.NGS + 2*GridData.DM.Nload + 1;
    end
    
    Volts = Vmagn_status.*exp(sqrt(-1)*Vph_status);
    %we update the status using delta
    if strcmp(GridData.type_of_model,'single_phase')==1

        if isfield(GridData,'rm_column') == 1
            if GridData.rm_column == 1
            Volts(1,1)=Volts(1,1)+delta(n);
            end
            Volts(1,1)=Volts(1,1)+delta(n);
            n=n+1;
            Volts(1,1)=Volts(1,1)+1i*delta(n);
        else
            Volts(1,1)=Volts(1,1)+delta(n);
        end
        Vmagn_status(1,1)=abs(Volts(1,1));
        Vph_status (1,1)=angle(Volts(1,1));
        
        for x = 2:GridData.Nodes_num
            n=n+1;
            Volts(x)=Volts(x)+delta(n);
            n=n+1;
            Volts(x,1)=Volts(x,1)+1i*delta(n);
            Vmagn_status(x,1)=abs(Volts(x,1));
            Vph_status (x,1)=angle(Volts(x,1));
        end %the state is updated
        
    elseif strcmp(GridData.type_of_model,'three_phase_sequence')==1  || strcmp(GridData.type_of_model,'three_phase_unbalance')==1  
        Vreal(1,1)=real(Volts(1,1))+delta(1); %at the slack bus we update only the magnitude because the phase angle is always zero;
        Volts(1,1)=Vreal(1,1);
        Vmagn_status(1,1)=abs(Volts(1,1));
        Vph_status (1,1)=angle(Volts(1,1));
        
        Vreal(2,1)=real(Volts(2,1))+delta(2);
        Volts(2,1)=Vreal(2,1)+1i*Vreal(2,1)*3/sqrt(3);
        Vmagn_status(2,1)=abs(Volts(2,1));
        Vph_status (2,1)=angle(Volts(2,1));
        
        Vreal(3,1) = real(Volts(3,1))+delta(3);
        Volts(3,1) = Vreal(3,1)+1i*Vreal(3,1)*-3/sqrt(3);
        Vmagn_status (3,1) = abs(Volts(3,1));
        Vph_status   (3,1) = angle(Volts(3,1));
        n = 3;
        for x = 2 : GridData.Nodes_num
            for f = 1 : 3
                if GridData.present_node(f,x) > 0
                    n = n + 1;
                    Volts(f,x) = Volts(f,x) + delta(n);
                    n = n + 1;
                    Volts(f,x) = Volts(f,x) + 1i*delta(n);
                end
                Vmagn_status(f,x) = abs(Volts(f,x));
                Vph_status  (f,x) = angle(Volts(f,x));
            end
        end       
    end
    % We calculate the maximum delta so that we verify if we need to stop the Newton Rapson iterations
    max_delta=max(abs(delta));
end
%based on the estimated voltages we calculate also the currents
if strcmp(GridData.type_of_model,'single_phase')==1
    I_branch = zeros(GridData.Lines_num,1);
    Volts = Vmagn_status.*exp(sqrt(-1)*Vph_status);
    for m=1:GridData.Lines_num
        n_i=GridData.topology(2,m);
        n_f=GridData.topology(3,m);
        V_i=Volts(n_i);
        V_f=Volts(n_f);
        R=GridData.R2(m);
        X=GridData.X2(m);
        B=GridData.B1(m);
        G=GridData.G1(m);
        I_branch(m) =  0.5*(G+1i*B)*(V_i+V_f) + (R+1i*X)*(V_i-V_f);
    end %branch currents %some problems using this type of calculation
    Imagn_status = abs(I_branch);
    Iph_status = phase(I_branch);
    Vph_status = wrapToPi(Vph_status);
    Iph_status = wrapToPi(Iph_status);
    
elseif strcmp(GridData.type_of_model,'three_phase_sequence')==1  || strcmp(GridData.type_of_model,'three_phase_unbalance')==1
    Imagn_status=zeros(3,GridData.Lines_num);
    Iph_status=zeros(3,GridData.Lines_num);
    I_branch=zeros(3,GridData.Lines_num);
    for m = 1 : GridData.Lines_num
        n_i=GridData.topology(2,m);
        n_f=GridData.topology(3,m);
        V_i = Volts(:,n_i);
        V_f = Volts(:,n_f);
        R=GridData.R2(:,3*m-2:3*m);
        X=GridData.X2(:,3*m-2:3*m);
        B=GridData.B1(:,3*m-2:3*m);
        G=GridData.G1(:,3*m-2:3*m);
        I_branch(:,m) =  0.5*(G+1i*B)*(V_i+V_f) +(R+1i*X)*(V_i-V_f); %there is the current going to the admittances at beginnend and end of the line
        Imagn_status(:,m)=abs(I_branch(:,m)); %amplitudes and phases of the branch currents are considered at the end of the line
        Iph_status(:,m)=phase(I_branch(:,m));
    end %branch currents %some problems using this type of calculation
    Vph_status = wrapToPi(Vph_status);
    Iph_status = wrapToPi(Iph_status);
end

if iteration == Test_SetUp.limit2 %in case we reach the maximum number of iterations
    max_delta;
end
end