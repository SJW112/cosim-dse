%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Code to calculate the h(x) vector for the VRIDSSE estimator. They are measurement matematically
% calculated based on the estimated state at the ith iteration
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function [hx]=calc_hx_VRIDSSE(Vmagn_status,Vph_status,GridData,inj_status)
% Steps:
% 1) Calculate the branch currents based on the voltage differences and the
% model-parameters of the lines
% 2) calculate the injection
% currents based on the branch currents and kirckoff law

if strcmp(GridData.type_of_model,'single_phase')==1
    hx=zeros(GridData.MeasNum,1);
    %calcualte branch currents
    I_branch=zeros(1,GridData.Lines_num);
    I_load=zeros(1,GridData.Nodes_num);
    Volts=Vmagn_status(:).*exp(sqrt(-1)*Vph_status(:));
    n_inj_status = 0;
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
    
    %calcualte injection currents
    for n=1:GridData.Nodes_num
        for m=1:GridData.Lines_num
            if GridData.topology(2,m)== n
                I_load(n) = I_load(n) - I_branch(GridData.topology(1,m));
            elseif GridData.topology(3,m)== n
                I_load(n) = I_load(n) + I_branch(GridData.topology(1,m));
            end
        end
    end
    
    % calculate h(x)
    for n=1:GridData.MeasNum
        if GridData.TypeMeas(n,1)==1 %real current
            hx(n,1)=real(I_load(GridData.LocationMeas(n,1)));
        end
        if GridData.TypeMeas(n,1)==2 %immaginary current
            hx(n,1)=imag(I_load(GridData.LocationMeas(n,1)));
        end
        if GridData.TypeMeas(n,1)==3 %voltage magnitude - translated to Vreal
            hx(n,1)=real(Volts(GridData.LocationMeas(n,1)));
        end
        if GridData.TypeMeas(n,1)==4 %voltage phase angle - translated to Vimag
            hx(n,1)=imag(Volts(GridData.LocationMeas(n,1)));
        end
        if GridData.TypeMeas(n,1)==5 %current magnitude - translated to Ireal
            hx(n,1)=real(I_branch(GridData.LocationMeas(n,1)));
        end
        if GridData.TypeMeas(n,1)==6 %current phase - translated to Iimag
            hx(n,1)=imag(I_branch(GridData.LocationMeas(n,1)));
        end
        if GridData.TypeMeas(n,1)==7 %pflow  - translated to Ireal
            hx(n,1)=real(I_branch(GridData.LocationMeas(n,1)));
        end
        if GridData.TypeMeas(n,1)==8 %qflow -  - translated to Ireal
            hx(n,1)=imag(I_branch(GridData.LocationMeas(n,1)));
        end
        if GridData.TypeMeas(n,1)==100 %dynamic state
            n_inj_status = n_inj_status +1;
            hx(n,1) = inj_status(n_inj_status,1) ;
        end
    end
elseif strcmp(GridData.type_of_model,'three_phase_sequence')==1  || strcmp(GridData.type_of_model,'three_phase_unbalance')==1
    hx=zeros(GridData.MeasNum,1);
    %calcualte branch currents
    I_branch=zeros(3,GridData.Lines_num);
    I_load=zeros(3,GridData.Nodes_num);
    Volts=zeros(3,GridData.Nodes_num);
    for x=1:GridData.Nodes_num
        for f=1:3
            Volts(f,x)=Vmagn_status(f,x).*exp(sqrt(-1)*Vph_status(f,x));
        end
    end
    for m=1:GridData.Lines_num
        n_i=GridData.topology(2,m);
        n_f=GridData.topology(3,m);
        V_i=Volts(:,n_i);
        V_f=Volts(:,n_f);
        R=GridData.R2(:,3*m-2:3*m);
        X=GridData.X2(:,3*m-2:3*m);
        B=GridData.B1(:,3*m-2:3*m);
        G=GridData.G1(:,3*m-2:3*m);
        I_branch(:,m) =  0.5*(G+1i*B)*(V_i+V_f) + (R+1i*X)*(V_i-V_f);
    end %branch currents %some problems using this type of calculation
    
    %calcualte injection currents
    for x=1:GridData.Nodes_num
        for m=1:GridData.Lines_num
            if GridData.topology(2,m)== x
                I_load(:,x) = I_load(:,x) - I_branch(:,GridData.topology(1,m));
            elseif GridData.topology(3,m)== x
                I_load(:,x) = I_load(:,x) + I_branch(:,GridData.topology(1,m));
            end
        end
    end
    
    % calculate h(x)
    for n=1:GridData.MeasNum
        if GridData.TypeMeas(n,1)==1 %real current
            hx(n,1)=real(I_load(GridData.PhaseMeas(n,1),GridData.LocationMeas(n,1)));
        end
        if GridData.TypeMeas(n,1)==2 %immaginary current
            hx(n,1)=imag(I_load(GridData.PhaseMeas(n,1),GridData.LocationMeas(n,1)));
        end
        if GridData.TypeMeas(n,1)==3 %voltage magnitude - translated to Vreal
            hx(n,1)=real(Volts(GridData.PhaseMeas(n,1),GridData.LocationMeas(n,1)));
        end
        if GridData.TypeMeas(n,1)==4 %voltage phase angle - translated to Vimag
            hx(n,1)=imag(Volts(GridData.PhaseMeas(n,1),GridData.LocationMeas(n,1)));
        end
        if GridData.TypeMeas(n,1)==5 %current magnitude - translated to Ireal
            hx(n,1)=real(I_branch(GridData.PhaseMeas(n,1),GridData.LocationMeas(n,1)));
        end
        if GridData.TypeMeas(n,1)==6 %current phase - translated to Iimag
            hx(n,1)=imag(I_branch(GridData.PhaseMeas(n,1),GridData.LocationMeas(n,1)));
        end
        if GridData.TypeMeas(n,1)==7 %pflow  - translated to Ireal
            hx(n,1)=real(I_branch(GridData.PhaseMeas(n,1),GridData.LocationMeas(n,1)));
        end
        if GridData.TypeMeas(n,1)==8 %qflow -  - translated to Ireal
            hx(n,1)=imag(I_branch(GridData.PhaseMeas(n,1),GridData.LocationMeas(n,1)));
        end
    end
end
end
