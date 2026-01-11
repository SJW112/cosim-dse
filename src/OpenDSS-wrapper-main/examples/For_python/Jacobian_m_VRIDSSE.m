%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Calculate the Jacobian matrix for the Voltage Real Imaginary Distribution System State Estimator (VRIDSSE)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function   [H] = Jacobian_m_VRIDSSE(GridData)

if strcmp(GridData.type_of_model,'single_phase')==1
    R = GridData.R2; %this are actually the inverses of the resistances
    X = GridData.X2; %this are actually the inverses of the reactances
    B = GridData.B1;
    G = GridData.G1;
    
    if GridData.inj_status == 0
        H = zeros(GridData.MeasNum,2*GridData.Nodes_num);
        dim_state_inv = 0;
    else
        H = zeros(GridData.MeasNum, 11*GridData.DM.NGF+10*GridData.DM.NGS+2*GridData.DM.Nload + 2*GridData.Nodes_num);
        dim_state_inv = 11*GridData.DM.NGF+10*GridData.DM.NGS + 2*GridData.DM.Nload;
    end
    
    
    for n = 1 : GridData.MeasNum
        if GridData.TypeMeas(n,1) ==1 %active power measurements, both SM and pseudo
            for x = 1:GridData.Lines_num
                if GridData.topology(2,x) == GridData.LocationMeas(n,1) %initial node of the branch
                    H(n,dim_state_inv + 2*GridData.LocationMeas(n,1)-1)   = H(n,dim_state_inv + 2*GridData.LocationMeas(n,1)-1) - 0.5*G(1,x) - R(1,x);
                    H(n,dim_state_inv + 2*GridData.LocationMeas(n,1))     = H(n,dim_state_inv + 2*GridData.LocationMeas(n,1)  ) + 0.5*B(1,x) + X(1,x);
                    H(n,dim_state_inv + 2*GridData.topology(3,x)-1)       = - 0.5*G(1,x) + R(1,x);
                    H(n,dim_state_inv + 2*GridData.topology(3,x))         = + 0.5*B(1,x) - X(1,x);
                    
                    
                elseif GridData.topology(3,x) == GridData.LocationMeas(n,1) %final node of the branch
                    H(n,dim_state_inv + 2*GridData.LocationMeas(n,1)-1)   = H(n,dim_state_inv + 2*GridData.LocationMeas(n,1)-1) + 0.5*G(1,x) - R(1,x);
                    H(n,dim_state_inv + 2*GridData.LocationMeas(n,1))     = H(n,dim_state_inv + 2*GridData.LocationMeas(n,1)  ) - 0.5*B(1,x) + X(1,x);
                    H(n,dim_state_inv + 2*GridData.topology(2,x)-1)       = + 0.5*G(1,x) + R(1,x);
                    H(n,dim_state_inv + 2*GridData.topology(2,x))         = - 0.5*B(1,x) - X(1,x);
                    
                end
            end
        end
        
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        if GridData.TypeMeas(n,1) ==2 %reactive power measurements, both SM and pseudo
            for x = 1:GridData.Lines_num
                if GridData.topology(2,x) == GridData.LocationMeas(n,1) %initial node of the branch
                    
                    H(n,dim_state_inv + 2*GridData.LocationMeas(n,1)-1) = H(n,dim_state_inv + 2*GridData.LocationMeas(n,1)-1) - 0.5*B(1,x) - X(1,x);
                    H(n,dim_state_inv + 2*GridData.LocationMeas(n,1))   = H(n,dim_state_inv + 2*GridData.LocationMeas(n,1))   - 0.5*G(1,x) - R(1,x);
                    H(n,dim_state_inv + 2*GridData.topology(3,x)-1)     = -0.5*B(1,x)+ X(1,x);
                    H(n,dim_state_inv + 2*GridData.topology(3,x))       = - 0.5*G(1,x) + R(1,x);
                    
                elseif GridData.topology(3,x ) == GridData.LocationMeas(n,1) %final node of the branch
                    H(n,dim_state_inv + 2*GridData.LocationMeas(n,1)-1) = H(n,dim_state_inv + 2*GridData.LocationMeas(n,1)-1) + 0.5*B(1,x) - X(1,x);
                    H(n,dim_state_inv + 2*GridData.LocationMeas(n,1))   = H(n,dim_state_inv + 2*GridData.LocationMeas(n,1)  ) + 0.5*G(1,x) - R(1,x);
                    H(n,dim_state_inv + 2*GridData.topology(2,x)-1)     = + 0.5*B(1,x) + X(1,x);
                    H(n,dim_state_inv + 2*GridData.topology(2,x))       = + 0.5*G(1,x) + R(1,x);
                    
                end
            end
        end
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        if GridData.TypeMeas(n,1) ==3 %voltage magnitude measurements - converted to real voltage
            %dV_re_i_1/dV_re_i_1
            H(n,dim_state_inv + 2*GridData.LocationMeas(n,1)-1) = 1;
            
            
            
        end
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        if GridData.TypeMeas(n,1) ==4 %voltage phase angle measurements - converted to imaginary voltage
            %dV_im_i_1/dV_im_i_1
            H(n,dim_state_inv + 2*GridData.LocationMeas(n,1)) = 1;
            
            
        end
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        if GridData.TypeMeas(n,1) ==5 %current magnitude measurements - converted to real current
            fin1 = GridData.topology(3,GridData.LocationMeas(n,1));
            in1 = GridData.topology(2,GridData.LocationMeas(n,1)) ;
            H(n,dim_state_inv + 2*in1-1)  =   0.5*G(1,GridData.LocationMeas(n,1))+R(1,GridData.LocationMeas(n,1));
            H(n,dim_state_inv + 2*in1)    = - 0.5*B(1,GridData.LocationMeas(n,1))-X(1,GridData.LocationMeas(n,1));
            H(n,dim_state_inv + 2*fin1-1) = - 0.5*G(1,GridData.LocationMeas(n,1))-R(1,GridData.LocationMeas(n,1));
            H(n,dim_state_inv + 2*fin1)   =   0.5*B(1,GridData.LocationMeas(n,1))+X(1,GridData.LocationMeas(n,1));
            
            
        end
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        if GridData.TypeMeas(n,1) ==6 %current phase measurements - converted to imaginary current
            fin1 = GridData.topology(3,GridData.LocationMeas(n,1));
            in1 = GridData.topology(2,GridData.LocationMeas(n,1)) ;
            H(n,dim_state_inv + 2*in1-1)  =   0.5*B(1,GridData.LocationMeas(n,1))+X(1,GridData.LocationMeas(n,1));
            H(n,dim_state_inv + 2*in1)    =   0.5*G(1,GridData.LocationMeas(n,1))+R(1,GridData.LocationMeas(n,1));
            H(n,dim_state_inv + 2*fin1-1) = - 0.5*B(1,GridData.LocationMeas(n,1))-X(1,GridData.LocationMeas(n,1));
            H(n,dim_state_inv + 2*fin1)   = - 0.5*G(1,GridData.LocationMeas(n,1))-R(1,GridData.LocationMeas(n,1));
            
        end
        
        if GridData.TypeMeas(n,1) ==7 %active power flow measurements
            fin1 = GridData.topology(3,GridData.LocationMeas(n,1));
            in1 = GridData.topology(2,GridData.LocationMeas(n,1)) ;
            H(n,dim_state_inv + 2*in1-1) =   0.5*G(1,GridData.LocationMeas(n,1))+R(1,GridData.LocationMeas(n,1));
            H(n,dim_state_inv + 2*in1)   = - 0.5*B(1,GridData.LocationMeas(n,1))-X(1,GridData.LocationMeas(n,1));
            H(n,dim_state_inv + 2*fin1-1) = - 0.5*G(1,GridData.LocationMeas(n,1))-R(1,GridData.LocationMeas(n,1));
            H(n,dim_state_inv + 2*fin1) =    0.5*B(1,GridData.LocationMeas(n,1))+X(1,GridData.LocationMeas(n,1));
            
        end
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        if GridData.TypeMeas(n,1) ==8 %reactive power flow measurements
            fin1 = GridData.topology(3,GridData.LocationMeas(n,1));
            in1 = GridData.topology(2,GridData.LocationMeas(n,1)) ;
            H(n,dim_state_inv + 2*in1-1)  =   0.5*B(1,GridData.LocationMeas(n,1))+X(1,GridData.LocationMeas(n,1));
            H(n,dim_state_inv + 2*in1)    =   0.5*G(1,GridData.LocationMeas(n,1))+R(1,GridData.LocationMeas(n,1));
            H(n,dim_state_inv + 2*fin1-1) = - 0.5*B(1,GridData.LocationMeas(n,1))-X(1,GridData.LocationMeas(n,1));
            H(n,dim_state_inv + 2*fin1)   = - 0.5*G(1,GridData.LocationMeas(n,1))-R(1,GridData.LocationMeas(n,1));
            
        end
        if GridData.TypeMeas(n,1)==100
            H(n,+ GridData.LocationMeas(n,1)) =  1; %dynamic state
        end
    end
    %the imaginary part of the slack bus is not a state (phase angle = 0),
    %therefore it can be deleted
    if isfield(GridData,'rm_column') == 1
        if GridData.rm_column == 1
            H(:,dim_state_inv + 2)=[];
        end
    else
        H(:,dim_state_inv + 2)=[];
    end
    
elseif strcmp(GridData.type_of_model,'three_phase_sequence')==1 || strcmp(GridData.type_of_model,'three_phase_unbalance')==1
    
    R=GridData.R2; %this are actually the inverses of the resistances
    X=GridData.X2; %this are actually the inverses of the reactances
    B=GridData.B1;
    G=GridData.G1;
    H = zeros(GridData.MeasNum, 6*GridData.Nodes_num);
    
    for n = 1 : GridData.MeasNum
        if GridData.TypeMeas(n,1) ==1 %active power measurements, both SM and pseudo
            for x = 1:GridData.Lines_num
                f = GridData.PhaseMeas(n,1);
                if GridData.PhaseMeas(n,1)==1; a=2; b=3; end
                if GridData.PhaseMeas(n,1)==2; a=1; b=3; end
                if GridData.PhaseMeas(n,1)==3; a=1; b=2; end
                
                if GridData.topology(2,x) == GridData.LocationMeas(n,1) %initial node of the branch
                    H(n,6*(GridData.LocationMeas(n,1)-1)+2*(f-1)+1)   = H(n,6*(GridData.LocationMeas(n,1)-1)+2*(f-1)+1) - 0.5*G(f,3*(x-1)+f) - R(f,3*(x-1)+f);
                    H(n,6*(GridData.LocationMeas(n,1)-1)+2*(a-1)+1)   = H(n,6*(GridData.LocationMeas(n,1)-1)+2*(a-1)+1) - 0.5*G(f,3*(x-1)+a) - R(f,3*(x-1)+a);
                    H(n,6*(GridData.LocationMeas(n,1)-1)+2*(b-1)+1)   = H(n,6*(GridData.LocationMeas(n,1)-1)+2*(b-1)+1) - 0.5*G(f,3*(x-1)+b) - R(f,3*(x-1)+b);
                    
                    H(n,6*(GridData.LocationMeas(n,1)-1)+2*f)     = H(n,6*(GridData.LocationMeas(n,1)-1)+2*f) + 0.5*B(f,3*(x-1)+f) + X(f,3*(x-1)+f);
                    H(n,6*(GridData.LocationMeas(n,1)-1)+2*a)     = H(n,6*(GridData.LocationMeas(n,1)-1)+2*a) + 0.5*B(f,3*(x-1)+a) + X(f,3*(x-1)+a);
                    H(n,6*(GridData.LocationMeas(n,1)-1)+2*b)     = H(n,6*(GridData.LocationMeas(n,1)-1)+2*b) + 0.5*B(f,3*(x-1)+b) + X(f,3*(x-1)+b);
                    
                    H(n,6*(GridData.topology(3,x)-1)+2*(f-1)+1)       = - 0.5*G(f,3*(x-1)+f) + R(f,3*(x-1)+f);
                    H(n,6*(GridData.topology(3,x)-1)+2*(a-1)+1)       = - 0.5*G(f,3*(x-1)+a) + R(f,3*(x-1)+a);
                    H(n,6*(GridData.topology(3,x)-1)+2*(b-1)+1)       = - 0.5*G(f,3*(x-1)+b) + R(f,3*(x-1)+b);
                    
                    H(n,6*(GridData.topology(3,x)-1)+2*f)         = + 0.5*B(f,3*(x-1)+f) - X(f,3*(x-1)+f);
                    H(n,6*(GridData.topology(3,x)-1)+2*a)         = + 0.5*B(f,3*(x-1)+a) - X(f,3*(x-1)+a);
                    H(n,6*(GridData.topology(3,x)-1)+2*b)         = + 0.5*B(f,3*(x-1)+b) - X(f,3*(x-1)+b);
                    
                elseif GridData.topology(3,x) == GridData.LocationMeas(n,1) %final node of the branch
                    H(n,6*(GridData.LocationMeas(n,1)-1)+2*(f-1)+1)   = H(n,6*(GridData.LocationMeas(n,1)-1)+2*(f-1)+1) + 0.5*G(f,3*(x-1)+f) - R(f,3*(x-1)+f);
                    H(n,6*(GridData.LocationMeas(n,1)-1)+2*(a-1)+1)   = H(n,6*(GridData.LocationMeas(n,1)-1)+2*(a-1)+1) + 0.5*G(f,3*(x-1)+a) - R(f,3*(x-1)+a);
                    H(n,6*(GridData.LocationMeas(n,1)-1)+2*(b-1)+1)   = H(n,6*(GridData.LocationMeas(n,1)-1)+2*(b-1)+1) + 0.5*G(f,3*(x-1)+b) - R(f,3*(x-1)+b);
                    
                    H(n,6*(GridData.LocationMeas(n,1)-1)+2*f)     = H(n,6*(GridData.LocationMeas(n,1)-1)+2*f) - 0.5*B(f,3*(x-1)+f) + X(f,3*(x-1)+f);
                    H(n,6*(GridData.LocationMeas(n,1)-1)+2*a)     = H(n,6*(GridData.LocationMeas(n,1)-1)+2*a) - 0.5*B(f,3*(x-1)+a) + X(f,3*(x-1)+a);
                    H(n,6*(GridData.LocationMeas(n,1)-1)+2*b)     = H(n,6*(GridData.LocationMeas(n,1)-1)+2*b) - 0.5*B(f,3*(x-1)+b) + X(f,3*(x-1)+b);
                    
                    H(n,6*(GridData.topology(2,x)-1)+2*(f-1)+1)       = + 0.5*G(f,3*(x-1)+f) + R(f,3*(x-1)+f);
                    H(n,6*(GridData.topology(2,x)-1)+2*(a-1)+1)       = + 0.5*G(f,3*(x-1)+a) + R(f,3*(x-1)+a);
                    H(n,6*(GridData.topology(2,x)-1)+2*(b-1)+1)       = + 0.5*G(f,3*(x-1)+b) + R(f,3*(x-1)+b);
                    
                    H(n,6*(GridData.topology(2,x)-1)+2*f)         = - 0.5*B(f,3*(x-1)+f) - X(f,3*(x-1)+f);
                    H(n,6*(GridData.topology(2,x)-1)+2*a)         = - 0.5*B(f,3*(x-1)+a) - X(f,3*(x-1)+a);
                    H(n,6*(GridData.topology(2,x)-1)+2*b)         = - 0.5*B(f,3*(x-1)+b) - X(f,3*(x-1)+b);
                end
                
            end
        end
        
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        if GridData.TypeMeas(n,1) == 2 %reactive power measurements, both SM and pseudo
            for x = 1:GridData.Lines_num
                
                f = GridData.PhaseMeas(n,1);
                if GridData.PhaseMeas(n,1)==1; a=2; b=3; end
                if GridData.PhaseMeas(n,1)==2; a=1; b=3; end
                if GridData.PhaseMeas(n,1)==3; a=1; b=2; end
                
                if GridData.topology(2,x) == GridData.LocationMeas(n,1) %initial node of the branch
                    H(n,6*(GridData.LocationMeas(n,1)-1)+2*(f-1)+1)   = H(n,6*(GridData.LocationMeas(n,1)-1)+2*(f-1)+1) - 0.5*B(f,3*(x-1)+f) - X(f,3*(x-1)+f);
                    H(n,6*(GridData.LocationMeas(n,1)-1)+2*(a-1)+1)   = H(n,6*(GridData.LocationMeas(n,1)-1)+2*(a-1)+1) - 0.5*B(f,3*(x-1)+a) - X(f,3*(x-1)+a);
                    H(n,6*(GridData.LocationMeas(n,1)-1)+2*(b-1)+1)   = H(n,6*(GridData.LocationMeas(n,1)-1)+2*(b-1)+1) - 0.5*B(f,3*(x-1)+b) - X(f,3*(x-1)+b);
                    
                    H(n,6*(GridData.LocationMeas(n,1)-1)+2*f)     = H(n,6*(GridData.LocationMeas(n,1)-1)+2*f) - 0.5*G(f,3*(x-1)+f) - R(f,3*(x-1)+f);
                    H(n,6*(GridData.LocationMeas(n,1)-1)+2*a)     = H(n,6*(GridData.LocationMeas(n,1)-1)+2*a) - 0.5*G(f,3*(x-1)+a) - R(f,3*(x-1)+a);
                    H(n,6*(GridData.LocationMeas(n,1)-1)+2*b)     = H(n,6*(GridData.LocationMeas(n,1)-1)+2*b) - 0.5*G(f,3*(x-1)+b) - R(f,3*(x-1)+b);
                    
                    H(n,6*(GridData.topology(3,x)-1)+2*(f-1)+1)       = - 0.5*B(f,3*(x-1)+f) + X(f,3*(x-1)+f);
                    H(n,6*(GridData.topology(3,x)-1)+2*(a-1)+1)       = - 0.5*B(f,3*(x-1)+a) + X(f,3*(x-1)+a);
                    H(n,6*(GridData.topology(3,x)-1)+2*(b-1)+1)       = - 0.5*B(f,3*(x-1)+b) + X(f,3*(x-1)+b);
                    
                    H(n,6*(GridData.topology(3,x)-1)+2*f)         = - 0.5*G(f,3*(x-1)+f) + R(f,3*(x-1)+f);
                    H(n,6*(GridData.topology(3,x)-1)+2*a)         = - 0.5*G(f,3*(x-1)+a) + R(f,3*(x-1)+a);
                    H(n,6*(GridData.topology(3,x)-1)+2*b)         = - 0.5*G(f,3*(x-1)+b) + R(f,3*(x-1)+b);
                    
                elseif GridData.topology(3,x) == GridData.LocationMeas(n,1) %final node of the branch
                    H(n,6*(GridData.LocationMeas(n,1)-1)+2*(f-1)+1)   = H(n,6*(GridData.LocationMeas(n,1)-1)+2*(f-1)+1) + 0.5*B(f,3*(x-1)+f) - X(f,3*(x-1)+f);
                    H(n,6*(GridData.LocationMeas(n,1)-1)+2*(a-1)+1)   = H(n,6*(GridData.LocationMeas(n,1)-1)+2*(a-1)+1) + 0.5*B(f,3*(x-1)+a) - X(f,3*(x-1)+a);
                    H(n,6*(GridData.LocationMeas(n,1)-1)+2*(b-1)+1)   = H(n,6*(GridData.LocationMeas(n,1)-1)+2*(b-1)+1) + 0.5*B(f,3*(x-1)+b) - X(f,3*(x-1)+b);
                    
                    H(n,6*(GridData.LocationMeas(n,1)-1)+2*f)     = H(n,6*(GridData.LocationMeas(n,1)-1)+2*f) + 0.5*G(f,3*(x-1)+f) - R(f,3*(x-1)+f);
                    H(n,6*(GridData.LocationMeas(n,1)-1)+2*a)     = H(n,6*(GridData.LocationMeas(n,1)-1)+2*a) + 0.5*G(f,3*(x-1)+a) - R(f,3*(x-1)+a);
                    H(n,6*(GridData.LocationMeas(n,1)-1)+2*b)     = H(n,6*(GridData.LocationMeas(n,1)-1)+2*b) + 0.5*G(f,3*(x-1)+b) - R(f,3*(x-1)+b);
                    
                    H(n,6*(GridData.topology(2,x)-1)+2*(f-1)+1)       = + 0.5*B(f,3*(x-1)+f) + X(f,3*(x-1)+f);
                    H(n,6*(GridData.topology(2,x)-1)+2*(a-1)+1)       = + 0.5*B(f,3*(x-1)+a) + X(f,3*(x-1)+a);
                    H(n,6*(GridData.topology(2,x)-1)+2*(b-1)+1)       = + 0.5*B(f,3*(x-1)+b) + X(f,3*(x-1)+b);
                    
                    H(n,6*(GridData.topology(2,x)-1)+2*f)         = + 0.5*G(f,3*(x-1)+f) + R(f,3*(x-1)+f);
                    H(n,6*(GridData.topology(2,x)-1)+2*a)         = + 0.5*G(f,3*(x-1)+a) + R(f,3*(x-1)+a);
                    H(n,6*(GridData.topology(2,x)-1)+2*b)         = + 0.5*G(f,3*(x-1)+b) + R(f,3*(x-1)+b);
                end
                
            end
        end
        
        
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        if GridData.TypeMeas(n,1) ==3 %voltage magnitude measurements - converted to real voltage
            %dV_re_i_1/dV_re_i_1
            H(n,6*(GridData.LocationMeas(n,1)-1)+2*(GridData.PhaseMeas(n,1)-1)+1)= 1;
        end
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        if GridData.TypeMeas(n,1) ==4 %voltage phase angle measurements - converted to imaginary voltage
            %dV_im_i_1/dV_im_i_1
            H(n,6*(GridData.LocationMeas(n,1)-1)+2*GridData.PhaseMeas(n,1))= 1;
        end
        
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        if GridData.TypeMeas(n,1) ==5 %current magnitude measurements - converted to real current
            fin1 = GridData.topology(3,GridData.LocationMeas(n,1));
            in1 = GridData.topology(2,GridData.LocationMeas(n,1)) ;
            
            f = GridData.PhaseMeas(n,1);
            if GridData.PhaseMeas(n,1)==1; a=2; b=3; end
            if GridData.PhaseMeas(n,1)==2; a=1; b=3; end
            if GridData.PhaseMeas(n,1)==3; a=1; b=2; end
            
            H(n,6*(in1-1)+2*(f-1)+1)  =   0.5*G(f,3*(GridData.LocationMeas(n,1)-1)+f)+R(f,3*(GridData.LocationMeas(n,1)-1)+f);
            H(n,6*(in1-1)+2*(a-1)+1)  =   0.5*G(f,3*(GridData.LocationMeas(n,1)-1)+a)+R(f,3*(GridData.LocationMeas(n,1)-1)+a);
            H(n,6*(in1-1)+2*(b-1)+1)  =   0.5*G(f,3*(GridData.LocationMeas(n,1)-1)+b)+R(f,3*(GridData.LocationMeas(n,1)-1)+b);
            
            H(n,6*(in1-1)+2*f)    = - 0.5*B(f,3*(GridData.LocationMeas(n,1)-1)+f)-X(f,3*(GridData.LocationMeas(n,1)-1)+f);
            H(n,6*(in1-1)+2*a)    = - 0.5*B(f,3*(GridData.LocationMeas(n,1)-1)+a)-X(f,3*(GridData.LocationMeas(n,1)-1)+a);
            H(n,6*(in1-1)+2*b)    = - 0.5*B(f,3*(GridData.LocationMeas(n,1)-1)+b)-X(f,3*(GridData.LocationMeas(n,1)-1)+b);
            
            H(n,6*(fin1-1)+2*(f-1)+1)  =  - 0.5*G(f,3*(GridData.LocationMeas(n,1)-1)+f)-R(f,3*(GridData.LocationMeas(n,1)-1)+f);
            H(n,6*(fin1-1)+2*(a-1)+1)  =  - 0.5*G(f,3*(GridData.LocationMeas(n,1)-1)+a)-R(f,3*(GridData.LocationMeas(n,1)-1)+a);
            H(n,6*(fin1-1)+2*(b-1)+1)  =  - 0.5*G(f,3*(GridData.LocationMeas(n,1)-1)+b)-R(f,3*(GridData.LocationMeas(n,1)-1)+b);
            
            H(n,6*(fin1-1)+2*f)    =  0.5*B(f,3*(GridData.LocationMeas(n,1)-1)+f)+X(f,3*(GridData.LocationMeas(n,1)-1)+f);
            H(n,6*(fin1-1)+2*a)    =  0.5*B(f,3*(GridData.LocationMeas(n,1)-1)+a)+X(f,3*(GridData.LocationMeas(n,1)-1)+a);
            H(n,6*(fin1-1)+2*b)    =  0.5*B(f,3*(GridData.LocationMeas(n,1)-1)+b)+X(f,3*(GridData.LocationMeas(n,1)-1)+b);
            
        end
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        if GridData.TypeMeas(n,1) ==6 %current phase measurements - converted to imaginary current
            fin1 = GridData.topology(3,GridData.LocationMeas(n,1));
            in1 = GridData.topology(2,GridData.LocationMeas(n,1)) ;
            f = GridData.PhaseMeas(n,1);
            if GridData.PhaseMeas(n,1)==1; a=2; b=3; end
            if GridData.PhaseMeas(n,1)==2; a=1; b=3; end
            if GridData.PhaseMeas(n,1)==3; a=1; b=2; end
            H(n,6*(in1-1)+2*(f-1)+1)  =   0.5*B(f,3*(GridData.LocationMeas(n,1)-1)+f)+X(f,3*(GridData.LocationMeas(n,1)-1)+f);
            H(n,6*(in1-1)+2*(a-1)+1)  =   0.5*B(f,3*(GridData.LocationMeas(n,1)-1)+a)+X(f,3*(GridData.LocationMeas(n,1)-1)+a);
            H(n,6*(in1-1)+2*(b-1)+1)  =   0.5*B(f,3*(GridData.LocationMeas(n,1)-1)+b)+X(f,3*(GridData.LocationMeas(n,1)-1)+b);
            
            H(n,6*(in1-1)+2*f)    =  0.5*G(f,3*(GridData.LocationMeas(n,1)-1)+f)+R(f,3*(GridData.LocationMeas(n,1)-1)+f);
            H(n,6*(in1-1)+2*a)    =  0.5*G(f,3*(GridData.LocationMeas(n,1)-1)+a)+R(f,3*(GridData.LocationMeas(n,1)-1)+a);
            H(n,6*(in1-1)+2*b)    =  0.5*G(f,3*(GridData.LocationMeas(n,1)-1)+b)+R(f,3*(GridData.LocationMeas(n,1)-1)+b);
            
            H(n,6*(fin1-1)+2*(f-1)+1)  =  - 0.5*B(f,3*(GridData.LocationMeas(n,1)-1)+f)-X(f,3*(GridData.LocationMeas(n,1)-1)+f);
            H(n,6*(fin1-1)+2*(a-1)+1)  =  - 0.5*B(f,3*(GridData.LocationMeas(n,1)-1)+a)-X(f,3*(GridData.LocationMeas(n,1)-1)+a);
            H(n,6*(fin1-1)+2*(b-1)+1)  =  - 0.5*B(f,3*(GridData.LocationMeas(n,1)-1)+b)-X(f,3*(GridData.LocationMeas(n,1)-1)+b);
            
            H(n,6*(fin1-1)+2*f)    = - 0.5*G(f,3*(GridData.LocationMeas(n,1)-1)+f)-R(f,3*(GridData.LocationMeas(n,1)-1)+f);
            H(n,6*(fin1-1)+2*a)    = - 0.5*G(f,3*(GridData.LocationMeas(n,1)-1)+a)-R(f,3*(GridData.LocationMeas(n,1)-1)+a);
            H(n,6*(fin1-1)+2*b)    = - 0.5*G(f,3*(GridData.LocationMeas(n,1)-1)+b)-R(f,3*(GridData.LocationMeas(n,1)-1)+b);
            
        end
        
        if GridData.TypeMeas(n,1) ==7 %active power flow measurements
            
            f = GridData.PhaseMeas(n,1);
            if GridData.PhaseMeas(n,1)==1; a=2; b=3; end
            if GridData.PhaseMeas(n,1)==2; a=1; b=3; end
            if GridData.PhaseMeas(n,1)==3; a=1; b=2; end
            
            H(n,6*(in1-1)+2*(f-1)+1)  =   0.5*G(f,3*(GridData.LocationMeas(n,1)-1)+f)+R(f,3*(GridData.LocationMeas(n,1)-1)+f);
            H(n,6*(in1-1)+2*(a-1)+1)  =   0.5*G(f,3*(GridData.LocationMeas(n,1)-1)+a)+R(f,3*(GridData.LocationMeas(n,1)-1)+a);
            H(n,6*(in1-1)+2*(b-1)+1)  =   0.5*G(f,3*(GridData.LocationMeas(n,1)-1)+b)+R(f,3*(GridData.LocationMeas(n,1)-1)+b);
            
            H(n,6*(in1-1)+2*f)    = - 0.5*B(f,3*(GridData.LocationMeas(n,1)-1)+f)-X(f,3*(GridData.LocationMeas(n,1)-1)+f);
            H(n,6*(in1-1)+2*a)    = - 0.5*B(f,3*(GridData.LocationMeas(n,1)-1)+a)-X(f,3*(GridData.LocationMeas(n,1)-1)+a);
            H(n,6*(in1-1)+2*b)    = - 0.5*B(f,3*(GridData.LocationMeas(n,1)-1)+b)-X(f,3*(GridData.LocationMeas(n,1)-1)+b);
            
            H(n,6*(fin1-1)+2*(f-1)+1)  =  - 0.5*G(f,3*(GridData.LocationMeas(n,1)-1)+f)-R(f,3*(GridData.LocationMeas(n,1)-1)+f);
            H(n,6*(fin1-1)+2*(a-1)+1)  =  - 0.5*G(f,3*(GridData.LocationMeas(n,1)-1)+a)-R(f,3*(GridData.LocationMeas(n,1)-1)+a);
            H(n,6*(fin1-1)+2*(b-1)+1)  =  - 0.5*G(f,3*(GridData.LocationMeas(n,1)-1)+b)-R(f,3*(GridData.LocationMeas(n,1)-1)+b);
            
            H(n,6*(fin1-1)+2*f)    =  0.5*B(f,3*(GridData.LocationMeas(n,1)-1)+f)+X(f,3*(GridData.LocationMeas(n,1)-1)+f);
            H(n,6*(fin1-1)+2*a)    =  0.5*B(f,3*(GridData.LocationMeas(n,1)-1)+a)+X(f,3*(GridData.LocationMeas(n,1)-1)+a);
            H(n,6*(fin1-1)+2*b)    =  0.5*B(f,3*(GridData.LocationMeas(n,1)-1)+b)+X(f,3*(GridData.LocationMeas(n,1)-1)+b);
            
        end
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        if GridData.TypeMeas(n,1) ==8 %reactive power flow measurements
            fin1 = GridData.topology(3,GridData.LocationMeas(n,1));
            in1 = GridData.topology(2,GridData.LocationMeas(n,1)) ;
            f = GridData.PhaseMeas(n,1);
            if GridData.PhaseMeas(n,1)==1; a=2; b=3; end
            if GridData.PhaseMeas(n,1)==2; a=1; b=3; end
            if GridData.PhaseMeas(n,1)==3; a=1; b=2; end
            H(n,6*(in1-1)+2*(f-1)+1)  =   0.5*B(f,3*(GridData.LocationMeas(n,1)-1)+f)+X(f,3*(GridData.LocationMeas(n,1)-1)+f);
            H(n,6*(in1-1)+2*(a-1)+1)  =   0.5*B(f,3*(GridData.LocationMeas(n,1)-1)+a)+X(f,3*(GridData.LocationMeas(n,1)-1)+a);
            H(n,6*(in1-1)+2*(b-1)+1)  =   0.5*B(f,3*(GridData.LocationMeas(n,1)-1)+b)+X(f,3*(GridData.LocationMeas(n,1)-1)+b);
            
            H(n,6*(in1-1)+2*f)    =  0.5*G(f,3*(GridData.LocationMeas(n,1)-1)+f)+R(f,3*(GridData.LocationMeas(n,1)-1)+f);
            H(n,6*(in1-1)+2*a)    =  0.5*G(f,3*(GridData.LocationMeas(n,1)-1)+a)+R(f,3*(GridData.LocationMeas(n,1)-1)+a);
            H(n,6*(in1-1)+2*b)    =  0.5*G(f,3*(GridData.LocationMeas(n,1)-1)+b)+R(f,3*(GridData.LocationMeas(n,1)-1)+b);
            
            H(n,6*(fin1-1)+2*(f-1)+1)  =  - 0.5*B(f,3*(GridData.LocationMeas(n,1)-1)+f)-X(f,3*(GridData.LocationMeas(n,1)-1)+f);
            H(n,6*(fin1-1)+2*(a-1)+1)  =  - 0.5*B(f,3*(GridData.LocationMeas(n,1)-1)+a)-X(f,3*(GridData.LocationMeas(n,1)-1)+a);
            H(n,6*(fin1-1)+2*(b-1)+1)  =  - 0.5*B(f,3*(GridData.LocationMeas(n,1)-1)+b)-X(f,3*(GridData.LocationMeas(n,1)-1)+b);
            
            H(n,6*(fin1-1)+2*f)    = - 0.5*G(f,3*(GridData.LocationMeas(n,1)-1)+f)-R(f,3*(GridData.LocationMeas(n,1)-1)+f);
            H(n,6*(fin1-1)+2*a)    = - 0.5*G(f,3*(GridData.LocationMeas(n,1)-1)+a)-R(f,3*(GridData.LocationMeas(n,1)-1)+a);
            H(n,6*(fin1-1)+2*b)    = - 0.5*G(f,3*(GridData.LocationMeas(n,1)-1)+b)-R(f,3*(GridData.LocationMeas(n,1)-1)+b);
            
        end
    end
    %the imaginary part of the slack bus is not a state (phase angle = 0),
    %therefore it can be deleted
    delete_1st_bus = [2,4,6];
    % also we delete the column of the missing phases
    delete_column = union(delete_1st_bus,GridData.missing_node_phase);
    H(:,3)=H(:,3)+3/sqrt(3)*H(:,4); % we delete the columns of the imaginary parts of the slack bus
    H(:,5)=H(:,5)-3/sqrt(3)*H(:,6);
    H(:,delete_column)=[];
end
end
