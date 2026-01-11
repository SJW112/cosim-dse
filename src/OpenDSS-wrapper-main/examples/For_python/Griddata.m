% Code to generate input_data of the grid for state estimation

function [GridData] = Griddata(IEEE13)

GridData = struct; %this struct contains all the static data of the grid
type_of_model = 'three_phase_unbalance';
%%
%*******************************************************************
%  grid : IEEE 13 grid
base_power = 1e8;%Watts
% base_voltage = 4160/sqrt(3);%Volts
% base_voltage =[2400*(ones(6,1));(480/sqrt(3))*(ones(3,1));2400*(ones(27,1))];
% base_voltage =[4160*sqrt(3)*3*(ones(3,1));2400*(ones(3,1));(480/sqrt(3))*(ones(3,1));2400*(ones(27,1))];
% base_voltage =[4160*sqrt(3)*9*(ones(3,1));2400*(ones(9,1));(480/sqrt(3))*(ones(3,1));2400*(ones(33,1))];
base_voltage =[4160*sqrt(3)*9*(ones(3,1));(4160/sqrt(3))*(ones(9,1));(480/sqrt(3))*(ones(3,1));(4160/sqrt(3))*(ones(33,1))];

Nodes =   1:1:16;
base_power=zeros(48,1);
base_power(1:3)=1e8;
base_power(4:end)=1e8;
impedance_factor  = (base_power./((base_voltage).^2));
% impedance_factor(1:3)=[];
%% Calculate the impedance matrix
Y=IEEE13.Y;
Y=Y.Y;
Z=inv(Y);
Z_all=insert_missing_Yphases(Z); % add the missing phases and branches
% Z_all(4:9,:)=[];
% Z_all(:,4:9)=[];
% Z_all(1:3,:)=[]; Z_all(:,1:3)=[];
R_all=real(Z_all).* impedance_factor;
X_all=imag(Z_all).* impedance_factor;
%%
% topology_initial_=[1,2,3;37,38,39;34,35,36;13,14,15;37,38,39;37,38,39;7,8,9;16,17,18;22,23,24;13,14,15;43,44,45;43,44,45;13,14,15]';
% topology_final_=[4,5,6;34,35,36;13,14,15;40,41,42; 7, 8, 9;16,17,18;10,11,12;19,20,21;25,26,27;43,44,45;28,29,30;31,32,33;22,23,24]';

% topology_initial=[1;2;14;13; 6;14;14; 4;7; 9; 6;16;16;6]';
% topology_final=  [2;3;13; 6;15; 4; 7; 5;8;10;16;11;12;9]';

topology_initial_=[1,2,3;4,5,6;40,41,42;37,38,39;16,17,18;40,41,42;40,41,42;10,11,12;19,20,21;25,26,27;16,17,18;46,47,48;46,47,48;16,17,18]';
topology_final_=[  4,5,6;7,8,9;37,38,39;16,17,18;43,44,45;10,11,12;19,20,21;13,14,15;22,23,24;28,29,30;46,47,48;31,32,33;34,35,36;25,26,27]';


topology_initial_a=topology_initial_(1,:);
topology_initial_b=topology_initial_(2,:);
topology_initial_c=topology_initial_(3,:);
topology_final_a=topology_final_(1,:);
topology_final_b=topology_final_(2,:);
topology_final_c=topology_final_(3,:);

for i=1:length(topology_initial_a)
Raa_= R_all(topology_initial_a(i),topology_final_a(i));
Rab_= R_all(topology_initial_a(i),topology_final_b(i));
Rac_= R_all(topology_initial_a(i),topology_final_c(i));
Rbb_= R_all(topology_initial_b(i),topology_final_b(i));
Rbc_= R_all(topology_initial_b(i),topology_final_c(i));
Rcc_= R_all(topology_initial_c(i),topology_final_c(i));

Xaa_=X_all(topology_initial_a(i),topology_final_a(i));
Xab_=X_all(topology_initial_a(i),topology_final_b(i));
Xac_=X_all(topology_initial_a(i),topology_final_c(i));
Xbb_=X_all(topology_initial_b(i),topology_final_b(i));
Xbc_=X_all(topology_initial_b(i),topology_final_c(i));
Xcc_=X_all(topology_initial_c(i),topology_final_c(i));

Raa(:,i)=Raa_;
Rab(:,i)=Rab_;
Rac(:,i)=Rac_;
Rbb(:,i)=Rbb_;
Rbc(:,i)=Rbc_;
Rcc(:,i)=Rcc_;

Xaa(:,i)=Xaa_;
Xab(:,i)=Xab_;
Xac(:,i)=Xac_;
Xbb(:,i)=Xbb_;
Xbc(:,i)=Xbc_;
Xcc(:,i)=Xcc_;
end

%SS 650 632 670 671 632 632 633 645 692 671 684 684 671
% 1   2  14  13   6  14  14   4   7   9   6  16  16   6
% 2 g60 670 671 680 633 645 634 646 675 684 611 652 692
% 2   3  13   6  15   4   7   5   8  10  16  11  12   9     

    % topology_initial=[1;13;12;5;13;13;3;6;8;5;15;15;5]';
    % topology_final=[2;12;5;14;3;6;4;7;9;15;10;11;8]';

    topology_initial=[1;2;14;13; 6;14;14; 4;7; 9; 6;16;16;6]';
    topology_final=  [2;3;13; 6;15; 4; 7; 5;8;10;16;11;12;9]';

%     topology_initial=topology_initial_;
%     topology_final=topology_final_;
    Nodes_num = length(Nodes); %number of nodes in the grid
    Lines_num = length(topology_initial);%number of lines in the grid
    topology = [[1:Lines_num];topology_initial;topology_final];
    
    %*******************************************************************
    
%     impedance_factor  = (base_power/((base_voltage)^2));
%     impedance_factor=1;
    R1 = zeros(3,3*Lines_num);
    X1 = zeros(3,3*Lines_num);
    B1 = zeros(3,3*Lines_num);
    G1 = zeros(3,3*Lines_num);
    R2 = zeros(3,3*Lines_num);
    X2 = zeros(3,3*Lines_num);
    
    %case three phase with three phase matrixes
    R1(1,[1:3:3*Lines_num]) = Raa(1:Lines_num);
    R1(1,[2:3:3*Lines_num]) = Rab(1:Lines_num);
    R1(2,[1:3:3*Lines_num]) = Rab(1:Lines_num);
    R1(1,[3:3:3*Lines_num]) = Rac(1:Lines_num);
    R1(3,[1:3:3*Lines_num]) = Rac(1:Lines_num);
    R1(2,[2:3:3*Lines_num]) = Rbb(1:Lines_num);
    R1(2,[3:3:3*Lines_num]) = Rbc(1:Lines_num);
    R1(3,[2:3:3*Lines_num]) = Rbc(1:Lines_num);
    R1(3,[3:3:3*Lines_num]) = Rcc(1:Lines_num);
    
    
    X1(1,[1:3:3*Lines_num]) = Xaa(1:Lines_num);
    X1(1,[2:3:3*Lines_num]) = Xab(1:Lines_num);
    X1(2,[1:3:3*Lines_num]) = Xab(1:Lines_num);
    X1(1,[3:3:3*Lines_num]) = Xac(1:Lines_num);
    X1(3,[1:3:3*Lines_num]) = Xac(1:Lines_num);
    X1(2,[2:3:3*Lines_num]) = Xbb(1:Lines_num);
    X1(2,[3:3:3*Lines_num]) = Xbc(1:Lines_num);
    X1(3,[2:3:3*Lines_num]) = Xbc(1:Lines_num);
    X1(3,[3:3:3*Lines_num]) = Xcc(1:Lines_num);
    
    present_node=zeros(3,Nodes_num);
    present_line=zeros(3,Lines_num);
    %based on the the three phase information (aa,bb,cc,ab,ac,bc) of the PI
    %models, some matrices based on the connection of [3x3] blocks are
    %built. THese 3x3 blocks are the R,X,B,G components of the PI model of
    %that particular line. Depending on the missing phases there could be
    %some zeros in the matrices.
    for x = 1 : Lines_num
        if (Raa(x) ~= 0 || Xaa(x) ~= 0)  && (Rbb(x) ~= 0 && Xbb(x) ~= 0) && (Rcc(x) ~= 0 || Xcc(x) ~= 0)
            %3phases
            Z1 = R1(:,3*(x-1)+1 :3*x) + 1i*X1(:,3*(x-1)+1 :3*x);
            R2(:,3*(x-1)+1 :3*x) = real(inv(Z1));
            X2(:,3*(x-1)+1 :3*x) = imag(inv(Z1));
            present_line(:,x)=[1;1;1];
            present_node(:,topology(2,x)) = present_node(:,topology(2,x)) + present_line(:,x);
            present_node(:,topology(3,x)) = present_node(:,topology(3,x)) + present_line(:,x);
        end
        if (Raa(x) ~= 0 || Xaa(x) ~= 0)  && (Rbb(x) ~= 0 || Xbb(x) ~= 0) && (Rcc(x) == 0 || Xcc(x) == 0)
            %2phases (A and B)
            Z1 = R1(1:2,3*(x-1)+1 :3*(x-1)+2) + 1i*X1(1:2,3*(x-1)+1 :3*(x-1)+2);
            R2(1:2,3*(x-1)+1 :3*(x-1)+2) = real(inv(Z1));
            X2(1:2,3*(x-1)+1 :3*(x-1)+2) = imag(inv(Z1));
            present_line(:,x)=[1;1;0];
            present_node(:,topology(2,x)) = present_node(:,topology(2,x)) + present_line(:,x);
            present_node(:,topology(3,x)) = present_node(:,topology(3,x)) + present_line(:,x);
        end
        if (Raa(x) ~= 0 || Xaa(x) ~= 0)  && (Rbb(x) == 0 || Xbb(x) == 0) && (Rcc(x) ~= 0 || Xcc(x) ~= 0)
            %2phases (A and C)
            Z1 = R1([1,3],[3*(x-1)+1,3*(x-1)+3]) + 1i*X1([1,3],[3*(x-1)+1,3*(x-1)+3]);
            R2([1,3],[3*(x-1)+1,3*(x-1)+3]) = real(inv(Z1));
            X2([1,3],[3*(x-1)+1,3*(x-1)+3]) = imag(inv(Z1));
            present_line(:,x)=[1;0;1];
            present_node(:,topology(2,x)) = present_node(:,topology(2,x)) + present_line(:,x);
            present_node(:,topology(3,x)) = present_node(:,topology(3,x)) + present_line(:,x);
        end
        if (Raa(x) == 0 || Xaa(x) == 0)  && (Rbb(x) ~= 0 || Xbb(x) ~= 0) && (Rcc(x) ~= 0 || Xcc(x) ~= 0)
            %2phases (B and C)
            Z1 = R1(2:3,3*(x-1)+2 :3*(x-1)+3) + 1i*X1(2:3,3*(x-1)+2 :3*(x-1)+3);
            R2(2:3,3*(x-1)+2 :3*(x-1)+3) = real(inv(Z1));
            X2(2:3,3*(x-1)+2 :3*(x-1)+3) = imag(inv(Z1));
            present_line(:,x)=[0;1;1];
            present_node(:,topology(2,x)) = present_node(:,topology(2,x)) + present_line(:,x);
            present_node(:,topology(3,x)) = present_node(:,topology(3,x)) + present_line(:,x);
        end
        if (Raa(x) ~= 0 || Xaa(x) ~= 0)  && (Rbb(x) == 0 && Xbb(x) == 0) && (Rcc(x) == 0 && Xcc(x)== 0)
            %1phases (A)
            Z1 = R1(1,3*(x-1)+1) + 1i*X1(1,3*(x-1)+1);
            R2(1,3*(x-1)+1) = real(inv(Z1));
            X2(1,3*(x-1)+1) = imag(inv(Z1));
            present_line(:,x)=[1;0;0];
            present_node(:,topology(2,x)) = present_node(:,topology(2,x)) + present_line(:,x);
            present_node(:,topology(3,x)) = present_node(:,topology(3,x)) + present_line(:,x);
        end
        if (Raa(x) == 0 || Xaa(x) == 0)  && (Rbb(x) ~= 0 && Xbb(x) ~= 0) && (Rcc(x) == 0 && Xcc(x) == 0)
            %1phases (b)
            Z1 = R1(2,3*(x-1)+2) + 1i*X1(2,3*(x-1)+2);
            R2(2,3*(x-1)+2) = real(inv(Z1));
            X2(2,3*(x-1)+2) = imag(inv(Z1));
            present_line(:,x)=[0;1;0];
            present_node(:,topology(2,x)) = present_node(:,topology(2,x)) + present_line(:,x);
            present_node(:,topology(3,x)) = present_node(:,topology(3,x)) + present_line(:,x);
        end
        if (Raa(x) == 0 || Xaa(x) == 0)  && (Rbb(x) == 0 && Xbb(x) == 0) && (Rcc(x) ~= 0 && Xcc(x) ~= 0)
            %1phases (C)
            Z1 = R1(3,3*(x-1)+3) + 1i*X1(3,3*(x-1)+3);
            R2(3,3*(x-1)+3) = real(inv(Z1));
            X2(3,3*(x-1)+3) = imag(inv(Z1));
            present_line(:,x)=[0;0;1];
            present_node(:,topology(2,x)) = present_node(:,topology(2,x)) + present_line(:,x);
            present_node(:,topology(3,x)) = present_node(:,topology(3,x)) + present_line(:,x);
        end
    end
    missing_node_phase = [];
    for x = 1 : Nodes_num
        for f = 1 : 3
            if present_node(f,x) == 0
                missing_node_phase = [missing_node_phase,6*(x-1)+2*(f-1)+1,6*(x-1)+2*f];
            end
        end
    end
    missing_line_phase = [];
    for x = 1 : Lines_num
        for f = 1 : 3
            if present_line(f,x) == 0
                missing_line_phase = [missing_line_phase,6+6*(x-1)+2*(f-1)+1,6+6*(x-1)+2*f];
            end
        end
    end
    missing_node_phase = sort(missing_node_phase);
    GridData.missing_node_phase = missing_node_phase;
    missing_line_phase = sort(missing_line_phase);
    GridData.missing_line_phase = missing_line_phase;
    GridData.present_node=present_node;
    GridData.present_line=present_line;

A=zeros(Lines_num,Nodes_num);%logic matrix M lines X N nodes with A(m,n) = 1 if the node n is supplied by the line m
for m = 1 : Lines_num
    for n = 1 : Nodes_num
        if topology(3,m)== n
            A(m,n) = 1;
        elseif topology(2,m) == n
            for t = 1 : Lines_num
                if A(t,topology(2,m)) == 1
                    A(t,topology(3,m)) = 1;
                end
            end
        end
    end
end

% rearrange the information in GridData struct
GridData.type_of_model = type_of_model;
GridData.Nodes_num = Nodes_num;
GridData.Lines_num = Lines_num;
GridData.topology = topology;
GridData.base_power = base_power;
GridData.base_voltage = base_voltage;
GridData.base_current = GridData.base_power./base_voltage;
GridData.base_impedance = GridData.base_voltage/GridData.base_current;
GridData.R1 = R1;
GridData.X1 = X1;
GridData.B1 = B1;
GridData.G1 = G1;
GridData.R2 = R2;
GridData.X2 = X2;
GridData.A  = A;
GridData.inj_status = 0;
end
