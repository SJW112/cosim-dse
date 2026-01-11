%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Function to calculate the weight matrix and the covariance matrices
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function [W,GridData,R] = Weightm(GridData,PowerData,Combination_devices,Accuracy)

LM = 1e-12; %minimum acceptable variance
Gx = 0;
if Combination_devices.Vph_measure(1,1) == 1
    Gx = Gx + 1;
end
    n = 0;
    LocationMeas = 0;
    TypeMeas = 0;
    W = 0; R = 0;
    
    for x = 1 : GridData.Nodes_num
        for f = 1 : 3
            if GridData.present_node(f,x) ~= 0
                if Combination_devices.P_measure(1,x)==1 %active power measurement
                    Rtemp = (Accuracy.Accuracy_P*PowerData.Pinj(f,x))^2;
                    if Rtemp < LM; Rtemp = LM; end
                    R(n+1,n+1) = Rtemp;
                    W(n+1,n+1) = Rtemp^-1;
                    n = n + 1;
                    LocationMeas(n,1) = x;
                    TypeMeas(n,1) = 1;% 1 represent measurements of type active power
                    PhaseMeas(n,1) = f;
                    DelayMeas(n,1) = Combination_devices.P_measure(2,x);
                    
                elseif Combination_devices.Pseudo_measure(1,x) == 1 %pseudo measurements, but we do not consider pseudo measurements at the slack bus
                    Rtemp = (Accuracy.Accuracy_pseudo*PowerData.Pinj(f,x))^2;
                    if Rtemp < LM; Rtemp = LM; end
                    R(n+1,n+1) = Rtemp;
                    W(n+1,n+1) = Rtemp^-1;
                    n = n + 1;
                    LocationMeas(n,1) = x;
                    TypeMeas(n,1) = 1;% 1 represent measurements of type active power
                    PhaseMeas(n,1) = f;
                    DelayMeas(n,1) = Combination_devices.Pseudo_measure(2,x);
                end
                
                if Combination_devices.Q_measure(1,x)==1%reactive power measurement
                    Rtemp = (Accuracy.Accuracy_Q*PowerData.Qinj(f,x))^+2;
                    if Rtemp < LM; Rtemp = LM; end
                    R(n+1,n+1) = Rtemp;
                    W(n+1,n+1) = Rtemp^-1;
                    n = n + 1;
                    LocationMeas(n,1) = x;
                    TypeMeas(n,1) = 2;% 2 represent measurements of type reactive power
                    PhaseMeas(n,1) = f;
                    DelayMeas(n,1) = Combination_devices.Q_measure(2,x);
                    
                elseif Combination_devices.Pseudo_measure(1,x) == 1 %pseudo measurements, but we do not consider pseudo measurements at the slack bus
                    Rtemp = (Accuracy.Accuracy_pseudo*PowerData.Qinj(f,x))^2;
                    if Rtemp < LM; Rtemp = LM; end
                    R(n+1,n+1) = Rtemp;
                    W(n+1,n+1) = Rtemp^-1;
                    n = n + 1;
                    LocationMeas(n,1) = x;
                    TypeMeas(n,1) = 2;% 2 represent measurements of type reactive power
                    PhaseMeas(n,1) = f;
                    DelayMeas(n,1) = Combination_devices.Pseudo_measure(2,x);
                end
                
                % voltage real part - here it is converted from the covariance of magnitude and phase angle
                if Combination_devices.Vmagn_measure(1,x)==1 && Combination_devices.Vph_measure(1,x)==1
                    if x == 1 % we remove the phase measurement from the first bus
                        rotV(1,1) = cos(PowerData.Vph(f,x));
                        Rtemp = rotV*((Accuracy.Accuracy_Vmagn*PowerData.Vmagn(f,x))^2)*rotV';
                        if Rtemp < LM; Rtemp = LM; end
                        R(n+1,n+1) = Rtemp;
                        W(n+1,n+1) = Rtemp^-1;
                        n = n + 1;
                        LocationMeas(n,1) = x;
                        TypeMeas(n,1) = 3;% 3 represent measurements of type voltage magnitude
                        PhaseMeas(n,1) = f;
                        DelayMeas(n,1) = Combination_devices.Vmagn_measure(2,x);
                    else
                        
                        rotV(1,1) = cos(PowerData.Vph(f,x));
                        rotV(1,2) =  - sin(PowerData.Vph(f,x))*PowerData.Vmagn(f,x) ;
                        rotV(2,1) = sin(PowerData.Vph(f,x)) ;
                        rotV(2,2) =   cos(PowerData.Vph(f,x))*PowerData.Vmagn(f,x);
                        
                        Rtemp = rotV*[(Accuracy.Accuracy_Vmagn*PowerData.Vmagn(f,x))^2, 0; 0 (Accuracy.Accuracy_Vph)^2]*rotV';
                        if Rtemp(1,1) < LM; Rtemp(1,1) = LM; end
                        if Rtemp(2,2) < LM; Rtemp(2,2) = LM; end
                        R(n+1:n+2,n+1:n+2) = Rtemp;
                        W(n+1:n+2,n+1:n+2)= Rtemp^-1;
                        
                        n=n+1;
                        LocationMeas(n,1) = x;
                        TypeMeas(n,1) = 3;% 4 represent measurements of type voltage magnitude
                        PhaseMeas(n,1) = f;
                        DelayMeas(n,1) = Combination_devices.Vmagn_measure(2,x);
                        n=n+1;
                        LocationMeas(n,1) = x;
                        TypeMeas(n,1) = 4;% 4 represent measurements of type voltage phase angle
                        PhaseMeas(n,1) = f;
                        DelayMeas(n,1) = Combination_devices.Vph_measure(2,x);
                    end
                end
            end
        end
    end
    % now we search for measurements in the lines
    for b = 1 : GridData.Lines_num
        for f = 1 : 3
            if GridData.present_line(f,b) ~= 0
                % Current real part - already converted from magnitude and phase angle
                if Combination_devices.Imagn_measure(1,b)~=0 && Combination_devices.Iph_measure(1,b)~=0
                    rotI(1,1) = cos(PowerData.Iph(f,b));
                    rotI(1,2) =  - sin(PowerData.Iph(f,b))*PowerData.Imagn(f,b) ;
                    rotI(2,1) = sin(PowerData.Iph(f,b)) ;
                    rotI(2,2) =   cos(PowerData.Iph(f,b))*PowerData.Imagn(f,b);
                    std_dev = [(Accuracy.Accuracy_Imagn*PowerData.Imagn(b))^2, 0; 0 (Accuracy.Accuracy_Iph)^2];
                    Rtemp = rotI * std_dev *(rotI');
                    if Rtemp(1,1) < LM; Rtemp(1,1) = LM; end
                    if Rtemp(2,2) < LM; Rtemp(2,2) = LM; end
                    R(n+1:n+2,n+1:n+2) = Rtemp;
                    W(n+1:n+2,n+1:n+2)= Rtemp^-1;
                    n=n+1;
                    LocationMeas(n,1) = b;
                    TypeMeas(n,1) = 5;% 5 represent measurements of type current magnitude
                    PhaseMeas(n,1) = f;
                    DelayMeas(n,1) = Combination_devices.Imagn_measure(2,b);
                    n=n+1;
                    LocationMeas(n,1)=b;
                    TypeMeas(n,1)=6;% 6 represent measurements of type current ph angle
                    PhaseMeas(n,1) = f;
                    DelayMeas(n,1) = Combination_devices.Iph_measure(2,b);
                end
                if Combination_devices.Pflow_measure(1,b)~=0
                    Rtemp = (Accuracy.Accuracy_Pflow*PowerData.Pflow(f,b))^2;
                    if Rtemp < LM; Rtemp = LM; end
                    R(n+1,n+1) = Rtemp;
                    W(n+1,n+1) = Rtemp^-1;
                    n = n + 1;
                    LocationMeas(n,1) = b;
                    TypeMeas(n,1) = 7;% 1 represent measurements of type active power
                    PhaseMeas(n,1) = f;
                    DelayMeas(n,1) = Combination_devices.Pflow_measure(2,b);
                end
                
                if Combination_devices.Qflow_measure(1,b)~=0
                    Rtemp = (Accuracy.Accuracy_Qflow*PowerData.Qflow(f,b))^2;
                    if Rtemp < LM; Rtemp = LM; end
                    R(n+1,n+1) = Rtemp;
                    W(n+1,n+1) = Rtemp^-1;
                    n = n + 1;
                    LocationMeas(n,1) = b;
                    TypeMeas(n,1) = 8;% 1 represent measurements of type active power
                    PhaseMeas(n,1) = f;
                    DelayMeas(n,1) = Combination_devices.Qflow_measure(2,b);
                end
            end
        end
    end
 GridData.PhaseMeas = PhaseMeas;

GridData.MeasNum = n;
GridData.TypeMeas = TypeMeas;
GridData.LocationMeas = LocationMeas;
GridData.DelayMeas = DelayMeas;

% GridData.
end
